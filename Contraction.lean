import Mathlib

namespace Monolithic102

def discreteUpdate (x alpha beta target : Int) : Int :=
  (1 - alpha * beta) * x + alpha * target

theorem discrete_fixed_point
    (x alpha beta target : Int) (h : target = beta * x) :
    discreteUpdate x alpha beta target = x := by
  simp [discreteUpdate, h]
  ring

theorem discrete_difference
    (x y alpha beta target : Int) :
    discreteUpdate x alpha beta target - discreteUpdate y alpha beta target
      = (1 - alpha * beta) * (x - y) := by
  simp [discreteUpdate]
  ring

theorem perturbation_propagation
    (x delta alpha beta target : Int) :
    discreteUpdate (x + delta) alpha beta target - discreteUpdate x alpha beta target
      = (1 - alpha * beta) * delta := by
  simp [discreteUpdate]
  ring

end Monolithic102
