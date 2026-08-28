/*
 * Copyright 2026 Duatic AG
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 * following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 * disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
 * following disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
 * products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <gtest/gtest.h>
#include <eigen3/Eigen/Core>

#include <cstddef>
#include <random>

#include "duatic_dynaarm_driver/kinematic_translation.hpp"

namespace duatic::dynaarm_driver::kinematics
{
namespace
{

// Upper bound (exclusive of sign, i.e. the magnitude) used to draw the pseudo-random per-joint
// maximum velocities / torques evaluated by the outer-hull random tests below.
constexpr double kMaxVelocityMagnitude = 20.0;
constexpr double kMaxTorqueMagnitude = 300.0;
// Number of pseudo-random abs_max samples drawn per test.
constexpr int kNumRandomSamples = 5;
// Fixed seed so the "random" samples are reproducible across runs.
constexpr std::uint32_t kRandomSeed = 42U;

using MappingFunctionPtr = Eigen::VectorXd (*)(const Eigen::VectorXd&);

/*!
 * Brute-force the outer hull (element-wise maximum absolute reachable value) of a serial-to-coupled
 * mapping function over a symmetric input hyper-rectangle [-abs_max, +abs_max].
 */
Eigen::VectorXd bruteForceOuterHull(MappingFunctionPtr mapping_fn, const Eigen::VectorXd& abs_max)
{
  const Eigen::Index size = abs_max.size();
  Eigen::VectorXd hull = Eigen::VectorXd::Zero(size);

  const std::size_t num_combinations = std::size_t{ 1 } << static_cast<std::size_t>(size);
  Eigen::VectorXd signed_input(size);

  for (std::size_t combination = 0; combination < num_combinations; ++combination) {
    for (Eigen::Index i = 0; i < size; ++i) {
      const bool use_positive_max = ((combination >> static_cast<std::size_t>(i)) & std::size_t{ 1 }) != 0U;
      signed_input(i) = use_positive_max ? abs_max(i) : -abs_max(i);
    }

    hull = hull.cwiseMax(mapping_fn(signed_input).cwiseAbs());
  }

  return hull;
}

void expectVectorsNear(const Eigen::VectorXd& lhs, const Eigen::VectorXd& rhs, double tolerance)
{
  ASSERT_EQ(lhs.size(), rhs.size());
  for (Eigen::Index i = 0; i < lhs.size(); ++i) {
    EXPECT_NEAR(lhs(i), rhs(i), tolerance) << "mismatch at index " << i;
  }
}

// Draws a vector of per-joint magnitudes, each element independently uniform in [0, max_magnitude).
Eigen::VectorXd randomAbsMax(std::mt19937& rng, double max_magnitude, Eigen::Index size)
{
  std::uniform_real_distribution<double> distribution(0.0, max_magnitude);

  Eigen::VectorXd abs_max(size);
  for (Eigen::Index i = 0; i < size; ++i) {
    abs_max(i) = distribution(rng);
  }
  return abs_max;
}

}  // namespace

// map_from_serial_to_coupled_coordinate_limits must return exactly the outer hull that
// map_from_serial_to_coupled_coordinates attains when driven with every combination of
// +/- a pseudo-random set of per-joint maximum velocities.
// cppcheck-suppress syntaxError  // cppcheck doesn't know the TEST() gtest macro
TEST(KinematicTranslationLimits, CoordinateLimitsOuterHullRandomTest)
{
  std::mt19937 rng(kRandomSeed);

  for (int sample = 0; sample < kNumRandomSamples; ++sample) {
    const Eigen::VectorXd max_velocity =
        randomAbsMax(rng, kMaxVelocityMagnitude, DynaArmKinematicsMapping::input_size());

    const Eigen::VectorXd brute_force_hull =
        bruteForceOuterHull(&DynaArmKinematicsMapping::map_from_serial_to_coupled_coordinates, max_velocity);
    const Eigen::VectorXd analytic_limits =
        DynaArmKinematicsMapping::map_from_serial_to_coupled_coordinate_limits(max_velocity);

    SCOPED_TRACE(::testing::Message() << "sample " << sample);
    expectVectorsNear(brute_force_hull, analytic_limits, 1e-9);
  }
}

// map_from_serial_to_coupled_torque_limits must return exactly the outer hull that
// map_from_serial_to_coupled_torques attains when driven with every combination of
// +/- a pseudo-random set of per-joint maximum torques.
TEST(KinematicTranslationLimits, TorqueLimitsOuterHullRandomTest)
{
  std::mt19937 rng(kRandomSeed);

  for (int sample = 0; sample < kNumRandomSamples; ++sample) {
    const Eigen::VectorXd max_torque = randomAbsMax(rng, kMaxTorqueMagnitude, DynaArmKinematicsMapping::input_size());

    const Eigen::VectorXd brute_force_hull =
        bruteForceOuterHull(&DynaArmKinematicsMapping::map_from_serial_to_coupled_torques, max_torque);
    const Eigen::VectorXd analytic_limits =
        DynaArmKinematicsMapping::map_from_serial_to_coupled_torque_limits(max_torque);

    SCOPED_TRACE(::testing::Message() << "sample " << sample);
    expectVectorsNear(brute_force_hull, analytic_limits, 1e-9);
  }
}

// A zero maximum velocity for every joint means the coupled joints can never move either.
TEST(KinematicTranslationLimits, CoordinateLimitsZeroInputTest)
{
  const Eigen::VectorXd zero_velocity = Eigen::VectorXd::Zero(DynaArmKinematicsMapping::input_size());

  const Eigen::VectorXd analytic_limits =
      DynaArmKinematicsMapping::map_from_serial_to_coupled_coordinate_limits(zero_velocity);

  expectVectorsNear(analytic_limits, zero_velocity, 1e-9);
}

// A zero maximum torque for every joint means the coupled joints can never be loaded either.
TEST(KinematicTranslationLimits, TorqueLimitsZeroInputTest)
{
  const Eigen::VectorXd zero_torque = Eigen::VectorXd::Zero(DynaArmKinematicsMapping::input_size());

  const Eigen::VectorXd analytic_limits =
      DynaArmKinematicsMapping::map_from_serial_to_coupled_torque_limits(zero_torque);

  expectVectorsNear(analytic_limits, zero_torque, 1e-9);
}

// Concrete, per-joint velocity limits
TEST(KinematicTranslationLimits, CoordinateLimitsUrdfValuesTest)
{
  Eigen::VectorXd max_velocity(DynaArmKinematicsMapping::input_size());
  max_velocity << 10.64, 10.64, 10.64, 13.647, 13.647, 13.647;

  Eigen::VectorXd expected_limits(DynaArmKinematicsMapping::input_size());
  expected_limits << 10.64, 10.64, 21.28, 13.647, 13.647, 13.647;

  const Eigen::VectorXd analytic_limits =
      DynaArmKinematicsMapping::map_from_serial_to_coupled_coordinate_limits(max_velocity);

  expectVectorsNear(analytic_limits, expected_limits, 1e-9);
}

// Concrete, per-joint effort (torque) limits
TEST(KinematicTranslationLimits, TorqueLimitsUrdfValuesTest)
{
  Eigen::VectorXd max_torque(DynaArmKinematicsMapping::input_size());
  max_torque << 120.0, 120.0, 120.0, 40.0, 40.0, 40.0;

  Eigen::VectorXd expected_limits(DynaArmKinematicsMapping::input_size());
  expected_limits << 120.0, 240.0, 120.0, 40.0, 40.0, 40.0;

  const Eigen::VectorXd analytic_limits =
      DynaArmKinematicsMapping::map_from_serial_to_coupled_torque_limits(max_torque);

  expectVectorsNear(analytic_limits, expected_limits, 1e-9);
}

}  // namespace duatic::dynaarm_driver::kinematics
