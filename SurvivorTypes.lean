import Mathlib

namespace Monolithic102

structure RecursiveSystem where
  State : Type
  Env : Type
  Model : Type
  stepState : State → Env → Model → State
  stepModel : Model → State → Env → Model

structure Acceptance where
  beatsBaseline : Prop
  falseAlarmOK : Prop
  computeOK : Prop
  replicated : Prop

def Acceptance.passes (a : Acceptance) : Prop :=
  a.beatsBaseline ∧ a.falseAlarmOK ∧ a.computeOK ∧ a.replicated

structure AdaptiveSystem where
  State : Type
  invariant : State → Prop
  acceptable : State → Prop

def restored {A : AdaptiveSystem} (old new : A.State) : Prop := new = old
def regenerated {A : AdaptiveSystem} (old new : A.State) : Prop :=
  new ≠ old ∧ A.acceptable new ∧ A.invariant new

end Monolithic102
