; Logic programming

;;; Overview:
;;; - single uniform database--fewer data structures
;;; - facts are represented as relations, can be used to deduce new facts
;;; - variables are "logic variables", bound by "unification", never change value
;;; - programmer gives constraints without specifying how to do the evaluation
;;; - "automatic backtracking" allows the programmer to specify multiple constraints,
;;;   and Prolog will try to find facts that satisfy all of them

;; Idea 1: Uniform database

;;; Data takes the form of a database of assertions, called "clauses", which come
;;; in two types: facts and rules.
;;; Facts state a relationship that holds between two objects
;;; Rules state contingent facts (predicates?)

;;; Two ways to procedurally interpret declarative forms:
;;; - backward-chaining: reasoning backwards from the goal to the premises
;;; - forward-chaining: reasoning forwards from the premises to a conclusion

;;; Prolog does backward chaining only.

;; Idea 2: Unification of logic variables

;;; Method for stating that a variable is equal to an expression or another variable.

(defconstant fail nil "Indicates pat-match failure")

(defconstant no-bindings '((t . t)))

(defparameter *occurs-check* t "Should we do the occurs check?")

(defun variable-p (x)
  "Is x a variable (a symbol beginning with ?)?"
  (and (symbolp x) (equal (char (symbol-name x) 0) #\?)))

(defun get-binding (var bindings)
  "Find a (variable . value) pair in a binding list."
  (assoc var bindings))

(defun binding-val (binding)
  "Get the value part of a single binding."
  (cdr binding))

(defun lookup (var bindings)
  "Get the value part (for var) from a binding list."
  (binding-val (get-binding var bindings)))

(defun extend-bindings (var val bindings)
  "Add a (var . value) pair to a binding list."
  (cons (cons var val)
	(if (equal bindings no-bindings)
	    nil
	    bindings)))

(defun match-variable (var input bindings)
  "Does VAR match input?  Uses (or updates) and returns bindings."
  (let ((binding (get-binding var bindings)))
    (cond ((not binding) (extend-bindings var input bindings))
	  ((equal input (binding-val binding)) bindings)
	  (t fail))))

(defun unify (x y &optional (bindings no-bindings))
  "See if x and y match with given bindings."
  (cond ((eq bindings fail) fail)
	((eql x y) bindings)
	((variable-p x) (unify-variable x y bindings))
	((variable-p y) (unify-variable y x bindings))
	((and (consp x) (consp y))
	 (unify (rest x) (rest y)
		(unify (first x) (first y) bindings)))
	(t fail)))

(defun unify-variable (var x bindings)
  "Unify var with x, using (and maybe extending) bindings."
  (cond ((get-binding var bindings)
	 (unify (lookup var bindings) x bindings))
	((and (variable-p x) (get-binding x bindings))
	 (unify var (lookup x bindings) bindings))
	((and *occurs-check* (occurs-check var x bindings))
	 fail)
	(t (extend-bindings var x bindings))))

(defun occurs-check (var x bindings)
  "Does var occur anywhere inside x? (infinite circular unification!)"
  (cond ((eq var x) t)
	((and (variable-p x) (get-binding x bindings))
	 (occurs-check var (lookup x bindings) bindings))
	((consp x) (or (occurs-check var (first x) bindings)
		       (occurs-check var (rest x) bindings)))
	(t nil)))

(defun subst-bindings (bindings x)
  "Substitute the value of variables in bindings into x, taking recursively
  bound variables into account."
  (cond ((eq bindings fail) fail)
	((eq bindings no-bindings) x)
	((and (variable-p x) (get-binding x bindings))
	 (subst-bindings bindings (lookup x bindings)))
	((atom x) x)
	(t (cons (subst-bindings bindings (car x))
		 (subst-bindings bindings (cdr x))))))

(defun unifier (x y)
  "Return something that unifies with both x and y (or fail)."
  (subst-bindings (unify x y) x))

;; represent clauses as (head . body)
(defun clause-head (clause) (first clause))
(defun clause-body (clause) (rest clause))

;; indexing--we interpret a clause as: to prove the head, prove the body.
;; so index on heads.

;; clauses are stored on the predicate's plist
;; DC: this is stupid. we can't reach the property list, it's some magical cloud thing
(defun get-clauses (pred) (get pred 'clauses))
(defun predicate (relation) (first relation))

(defvar *db-predicates* nil
  "A list of all predicates stored in the database.")

(defmacro <- (&rest clause)
  `(add-clause ',clause))

(defun add-clause (clause)
  "Add a clause to the database, indexed by head's predicate"
  ;; predicate must be a non-variable symbol.
  (let ((pred (predicate (clause-head clause))))
    (assert (and (symbolp pred) (not (variable-p pred))))
    (pushnew pred *db-predicates*)
    (setf (get pred 'clauses)
	  (nconc (get-clauses pred) (list clause)))
    pred))

(defun clear-db ()
  "Remove all clauses (for all predicates) from the data base."
  (mapc #'clear-predicate *db-predicates*))

(defun clear-predicate (predicate)
  "Remove the clauses for a single predicate."
  (setf (get predicate 'clauses) nil))

;; (defun prove (goal bindings)
;;   "Return a list of possible solutions to a goal."
;;   ;; To prove goal, first find candidate clauses.
;;   ;; For each candidate, check if goal unifies with the head of the clause.
;;   ;; If so, try to prove all the goals in the body of the clause.
;;   ;; --> for facts, there are no goals in the body, which means success.
;;   ;; --> for rules, goals in body are proved one at a time, propagating bindings.
;;   (mapcan #'(lambda (clause)
;; 	      (let ((new-clause (rename-variables clause)))
;; 		(prove-all (clause-body new-clause)
;; 			   (unify goal (clause-head new-clause) bindings))))
;; 	  (get-clauses (predicate goal))))

;; (defun prove-all (goals bindings)
;;   "Return a list of solutions to the conjunction of goals."
;;   (cond ((eq bindings fail) fail)
;; 	((null goals) (list bindings))
;; 	(t (mapcan #'(lambda (goal1-solution)
;; 		       (prove-all (rest goals) goal1-solution))
;; 		   (prove (first goals) bindings)))))

(defun rename-variables (x)
  "Replace all variables in x with new ones."
  (sublis (mapcar #'(lambda (var) (cons var (gensym (string var))))
		  (variables-in x))
	  x))

(defun variables-in (exp)
  "Return a list of all the variables in EXP."
  (unique-find-anywhere-if #'variable-p exp))

(defun unique-find-anywhere-if (predicate tree &optional found-so-far)
  "Return a list of leaves of tree satisfying predicate, with duplicates removed."
  (if (atom tree)
      (if (funcall predicate tree)
	  (adjoin tree found-so-far)
	  found-so-far)
      (unique-find-anywhere-if predicate
			       (first tree)
			       (unique-find-anywhere-if predicate
							(rest tree)
							found-so-far))))

(defmacro ?- (&rest goals) `(top-level-prove ',goals))

;; (defun top-level-prove (goals)
;;   "Prove the goals, and print variables readably."
;;   (show-prolog-solutions
;;    (variables-in goals)
;;    (prove-all goals no-bindings)))

(defun show-prolog-solutions (vars solutions)
  "Print the variables in each of the solutions."
  (if (null solutions)
      (format t "~&No.")
      (mapc #'(lambda (solution) (show-prolog-vars vars solution))
	    solutions))
  (values))

;; (defun show-prolog-vars (vars bindings)
;;   "Print each variable with its binding."
;;   (if (null vars)
;;       (format t "~&Yes")
;;       (dolist (var vars)
;; 	(format t "~&~a = ~a" var
;; 		(subst-bindings bindings var))))
;;   (princ ";"))

;; Idea 3: automatic backtracking (redefining prove and prove-all)

(defun prove-all (goals bindings)
  "Find a solution to the conjunction of goals."
  (cond ((eq bindings fail) fail)
	((null goals) bindings)
	(t (prove (first goals) bindings (rest goals)))))

(defun prove (goal bindings other-goals)
  "Return a list of possible solutions to goal."
  (let ((clauses (get-clauses (predicate goal))))
    (if (listp clauses)
	(some
	 #'(lambda (clause)
	     (let ((new-clause (rename-variables clause)))
	       (prove-all
		(append (clause-body new-clause) other-goals)
		(unify goal (clause-head new-clause) bindings))))
	 clauses)
	;; If clauses isn't a list, it might be a primitive function to call (atom)
	(funcall clauses (rest goal) bindings other-goals))))

(defun top-level-prove (goals)
  (prove-all `(,@goals (show-prolog-vars ,@(variables-in goals)))
	     no-bindings)
  (format t "~&No.")
  (values))

(defun show-prolog-vars (vars bindings other-goals)
  "Print each variable with its binding.
  Then ask the user if more solutions are desired."
  (if (null vars)
      (format t "~&Yes")
      (dolist (var vars)
	(format t "~&~a = ~a" var
		(subst-bindings bindings var))))
  (if (continue-p)
      fail
      (prove-all other-goals bindings)))

(setf (get 'show-prolog-vars 'clauses) 'show-prolog-vars)

(defun continue-p ()
  "Ask user if we should continue looking for solutions."
  (case (read-char)
    (#\; t)
    (#\. nil)
    (#\newline (continue-p))
    (otherwise
     (format t " Type ; to see more or . to stop")
     (continue-p))))

(defmacro <- (&rest clause)
  "Add a clause to the database."
  `(add-clause ',(replace-?-vars clause)))

(defmacro ?- (&rest goals)
  "Make a query and print answers."
  `(top-level-prove ',(replace-?-vars goals)))

(defun replace-?-vars (exp)
  "Replace any ? within exp with a var of the form ?123."
  (cond ((eq exp '?) (gensym "?"))
	((atom exp) exp)
	(t (cons (replace-?-vars (first exp))
		 (replace-?-vars (rest exp))))))
