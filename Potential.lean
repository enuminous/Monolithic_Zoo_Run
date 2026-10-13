import Mathlib

namespace Monolithic102

def potentialDerivative (phi mu nu : Int) : Int := -mu * phi + nu * phi^3
def deterministicCoherence (phi mu nu : Int) : Int := mu * phi - nu * phi^3

theorem negative_potential_derivative_eq_dynamics (phi mu nu : Int) :
    -potentialDerivative phi mu nu = deterministicCoherence phi mu nu := by
  simp [potentialDerivative, deterministicCoherence]
  ring

theorem gradient_bridge (dD dU dR lambda : Int)
    (h : dD = dU - lambda * dR) :
    -dD = -dU + lambda * dR := by
  rw [h]
  ring

theorem approximate_gradient_bridge
    (dD dU dR dQ lambda epsilon : Int)
    (h : dD = dU - lambda * dR + epsilon * dQ) :
    (-dD) - (-dU + lambda * dR) = -epsilon * dQ := by
  rw [h]
  ring

end Monolithic102
