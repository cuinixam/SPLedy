/**
 * @file
 */

#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "power_signal_processing.h"
}

#include "mockup_power_signal_processing.h"

/*!
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_PSP-001
 * tests: SWDD_PSP-001
 */
TEST(power_signal_processing, test_power_stays_off)
{
    CREATE_MOCK(mymock);

    EXPECT_CALL(mymock, RteGetPowerState()).Times(0);
    EXPECT_CALL(mymock, RteSetPowerState(_)).Times(0);
    EXPECT_CALL(mymock, RteGetPowerKeyPressedEvent()).Times(1).WillOnce(Return(FALSE));

    powerSignalProcessing();
}

/*!
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_PSP-002
 * tests: SWDD_PSP-002, SWDD_PSP-003
 */
TEST(power_signal_processing, test_power_toggles)
{
    CREATE_MOCK(mymock); // Assuming you have a mock creation macro

    // Starting with power state off and P key pressed once
    EXPECT_CALL(mymock, RteGetPowerState()).WillOnce(Return(POWER_STATE_OFF));
    EXPECT_CALL(mymock, RteGetPowerKeyPressedEvent()).WillOnce(Return(TRUE));
    EXPECT_CALL(mymock, RteSetPowerState(POWER_STATE_ON));
    powerSignalProcessing();

    // Press Power key again to toggle power state to off
    EXPECT_CALL(mymock, RteGetPowerState()).WillOnce(Return(POWER_STATE_ON));
    EXPECT_CALL(mymock, RteGetPowerKeyPressedEvent()).WillOnce(Return(TRUE));
    EXPECT_CALL(mymock, RteSetPowerState(POWER_STATE_OFF));
    powerSignalProcessing();

    // Press Power key once more to toggle power state back to on
    EXPECT_CALL(mymock, RteGetPowerState()).WillOnce(Return(POWER_STATE_OFF));
    EXPECT_CALL(mymock, RteGetPowerKeyPressedEvent()).WillOnce(Return(TRUE));
    EXPECT_CALL(mymock, RteSetPowerState(POWER_STATE_ON));
    powerSignalProcessing();
}
