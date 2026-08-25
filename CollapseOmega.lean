namespace Monolithic102

def omegaObjective (loss divergence recursion lambda gamma : Int) : Int :=
  loss + lambda * divergence - gamma * recursion

theorem omega_zero_regularizers (loss divergence recursion : Int) :
    omegaObjective loss divergence recursion 0 0 = loss := by
  simp [omegaObjective]

theorem divergence_scaling_algebra (lambda divergence scale : Int) :
    lambda * (scale * divergence) = (lambda * scale) * divergence := by
  ring

end Monolithic102
