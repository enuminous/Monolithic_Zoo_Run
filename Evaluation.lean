import SurvivorTypes
namespace Monolithic102

theorem acceptance_requires_baseline (a : Acceptance) (h : a.passes) :
    a.beatsBaseline := h.1
theorem acceptance_requires_false_alarm (a : Acceptance) (h : a.passes) :
    a.falseAlarmOK := h.2.1
theorem acceptance_requires_compute (a : Acceptance) (h : a.passes) :
    a.computeOK := h.2.2.1
theorem acceptance_requires_replication (a : Acceptance) (h : a.passes) :
    a.replicated := h.2.2.2

theorem no_acceptance_without_replication (a : Acceptance)
    (h : ¬ a.replicated) : ¬ a.passes := by
  intro hp
  exact h hp.2.2.2

theorem regeneration_preserves_invariant
    {A : AdaptiveSystem} {old new : A.State}
    (h : regenerated old new) : A.invariant new := h.2.2

end Monolithic102
