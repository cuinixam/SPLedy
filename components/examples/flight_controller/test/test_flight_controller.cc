/**
 * @file test_flight_controller.cc
 * @brief Unit and integration tests for flight_controller component, including direct testing of CheckAbort.
 */

#include <gtest/gtest.h>
#include <gmock/gmock.h>
using namespace testing;

extern "C"
{
#include "flight_controller.h"
#include "rte.h"
}

#include "mockup_examples_flight_controller.h"

struct CheckAbortParam
{
    boolean off_course;
    boolean abort_commanded;
    boolean valid_abort_command;
    boolean expected_result;
    const char *description;
};

inline std::ostream &operator<<(std::ostream &os, const CheckAbortParam &param)
{
    os << param.description;
    return os;
}

class CheckAbortParamTest : public TestWithParam<CheckAbortParam>
{
};

INSTANTIATE_TEST_SUITE_P(
    CheckAbortCases,
    CheckAbortParamTest,
    Values(
        CheckAbortParam{true, false, false, true, "Off course triggers abort"},
        CheckAbortParam{false, true, true, true, "Abort commanded and valid"},
        CheckAbortParam{false, true, false, false, "Abort commanded but not valid"},
        CheckAbortParam{false, false, false, false, "No abort, not off course"}));

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_FC-100
 * tests: SWDD_FC-100, SWDD_FC-101, SWDD_FC-102
 */
TEST_P(CheckAbortParamTest, ReturnsExpectedResult)
{
    const auto &param = GetParam();
    EXPECT_EQ(CheckAbort(param.off_course, param.abort_commanded, param.valid_abort_command), param.expected_result);
}

class FlightControllerParamTest : public TestWithParam<CheckAbortParam>
{
};

INSTANTIATE_TEST_SUITE_P(
    FlightControllerCases,
    FlightControllerParamTest,
    Values(
        CheckAbortParam{true, false, false, true, "Off course triggers abort"},
        CheckAbortParam{false, true, true, true, "Abort commanded and valid"},
        CheckAbortParam{false, true, false, false, "Abort commanded but not valid"},
        CheckAbortParam{false, false, false, false, "No abort, not off course"}));

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_FC-001
 * tests: SWDD_FC-100, SWDD_FC-101, SWDD_FC-102, SWDD_FC-103,
 *   SWDD_FC-200, SWDD_FC-201, SWDD_FC-202, SWDD_FC-203, SWDD_FC-204
 */
TEST_P(FlightControllerParamTest, SetsExpectedSelfDestructState)
{
    const auto &param = GetParam();

    CREATE_MOCK(mymock);
    // Set expectations for the mock RTE functions
    EXPECT_CALL(mymock, RteGetOffCourse(_))
        .WillOnce(SetArgPointee<0>(param.off_course));
    EXPECT_CALL(mymock, RteGetAbortCommanded())
        .WillOnce(Return(param.abort_commanded));
    EXPECT_CALL(mymock, RteGetValidAbortCommand())
        .WillOnce(Return(param.valid_abort_command));
    EXPECT_CALL(mymock, RteSetSelfDestructState(param.expected_result)).Times(1);

    // Call the flight controller runnable
    flightController();
}
