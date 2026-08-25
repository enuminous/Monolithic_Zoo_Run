namespace Monolithic102

theorem pow_two_mul (a n : Nat) :
    a ^ (2 * n) = (a ^ n) ^ 2 := by
  rw [Nat.mul_comm 2 n, pow_mul]

theorem pow_46_eq_pow_23_sq (a : Nat) :
    a ^ 46 = (a ^ 23) ^ 2 := by
  simpa using pow_two_mul a 23

end Monolithic102
