#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "autoconf.h"
#include "spled.h"
}

#include "mockup_variant_test.h"

TEST(Disco, holding_the_power_button_turns_the_light_green)
{
   RGBColor lightValue;
   CREATE_MOCK(mymock);

   EXPECT_CALL(mymock, ButtonInterfaceIsButtonPressed(_)).WillRepeatedly(Return(true));
   EXPECT_CALL(mymock, ledInterface()).Times(10);

   for (int i = 0; i < 10; i++)
   {
      spled();
   }

   ASSERT_EQ(POWER_STATE_ON, RteGetPowerState());
   RteGetLightValue(&lightValue);
   ASSERT_EQ(lightValue.green, 128);
}
