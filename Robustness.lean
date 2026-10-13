import Mathlib

namespace Monolithic102

def alarm (value threshold : Int) : Prop := threshold ≤ value

theorem alarm_translation_invariant (value threshold shift : Int) :
    alarm (value + shift) (threshold + shift) ↔ alarm value threshold := by
  simp [alarm]

theorem equal_score_not_state_equality :
    ∃ (x y : Int), x ≠ y ∧ x^2 = y^2 := by
  refine ⟨1, -1, ?_, ?_⟩
  · decide
  · norm_num

theorem multiplicative_gate_zero_left (a b : Int) :
    0 * a * b = 0 := by ring

end Monolithic102
