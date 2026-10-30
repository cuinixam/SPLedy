/**
 * @file
 */

#include <gtest/gtest.h>
using namespace testing;

extern "C"
{
#include "hello_gmock.h"
}

#include "mockup_examples_hello_gmock.h"

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_010
 * tests: SWDD_COMP_A-010
 */
TEST(hello_gmock_suite, get_interface)
{
    /* Arrange */
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, GetData())
        .WillOnce(Return(13));

    /* Act and Assert */
    ASSERT_EQ(13, CheckGetData());
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_020
 * tests: SWDD_COMP_A-020
 */
TEST(hello_gmock_suite, get_by_pointer)
{
    /* Arrange */
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, GetByPointer(_))
        .WillOnce(SetArgPointee<0>(42));

    /* Act and Assert */
    ASSERT_EQ(42, CheckGetByPointer());
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_030
 * tests: SWDD_COMP_A-030
 */
TEST(hello_gmock_suite, get_by_pointer_and_return_value)
{
    /* Arrange */
    int value = 0;
    CREATE_MOCK(mymock);
    // Set up the mock to return a value and set the pointed data
    EXPECT_CALL(mymock, GetByPointerAndReturnValue(_))
        .WillOnce(DoAll(SetArgPointee<0>(42), Return(2)));

    /* Act and Assert */
    ASSERT_EQ(2, CheckGetByPointerAndReturnValue(&value));
    ASSERT_EQ(42, value);
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_040
 * tests: SWDD_COMP_A-040
 */
TEST(hello_gmock_suite, get_data_structure_by_pointer)
{
    /* Arrange */
    MyDataType result = {0, 0};
    MyDataType input = {123, 42};
    CREATE_MOCK(mymock);
    // Set up the mock to fill the data structure
    EXPECT_CALL(mymock, GetDataStructureByPointer(_))
        .WillOnce(SetArgPointee<0>(input));

    // Act
    CheckGetDataStructureByPointer(&result);

    // Assert
    ASSERT_EQ(result.a, 123);
    ASSERT_EQ(result.b, 42);
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_041
 * tests: SWDD_COMP_A-040
 */
TEST(hello_gmock_suite, get_data_structure_by_pointer_1)
{
    /* Arrange */
    MyDataType result = {0, 0};
    CREATE_MOCK(mymock);
    // Set up the mock to fill the struct fields using a lambda
    // This is an alternative to SetArgPointee that allows more complex logic
    // to be executed when the mock is called.
    EXPECT_CALL(mymock, GetDataStructureByPointer(_))
        .WillOnce(Invoke([](MyDataType *data)
                         {
            data->a = 100+23;
            data->b = 21*2; }));

    // Act
    CheckGetDataStructureByPointer(&result);

    // Assert
    ASSERT_EQ(result.a, 123);
    ASSERT_EQ(result.b, 42);
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_050
 * tests: SWDD_COMP_A-050
 */
TEST(hello_gmock_suite, get_data_structure_array)
{
    /* Arrange */
    MyDataType result[2] = {{0, 0}, {0, 0}};
    MyDataType input[2] = {{123, 'a'}, {456, 'b'}};
    CREATE_MOCK(mymock);
    // Set up the mock to fill the data structure array
    EXPECT_CALL(mymock, GetDataStructureArray(_))
        .WillOnce(SetArrayArgument<0>(input, input + 2));

    // Act
    CheckGetDataStructureArray(result);

    // Assert
    ASSERT_EQ(result[0].a, 123);
    ASSERT_EQ(result[0].b, 'a');
    ASSERT_EQ(result[1].a, 456);
    ASSERT_EQ(result[1].b, 'b');
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_110
 * tests: SWDD_COMP_A-110
 */
TEST(hello_gmock_suite, set_data)
{
    /* Arrange */
    CREATE_MOCK(mymock);
    EXPECT_CALL(mymock, SetData(42))
        .Times(1);

    /* Act */
    CheckSetData(42);
}

/**
 * @trace {{ gtest.test }}
 * type: test
 * id: TS_COMP_A_120
 * tests: SWDD_COMP_A-120
 */
TEST(hello_gmock_suite, set_data_by_pointer)
{
    /* Arrange */
    CREATE_MOCK(mymock);
    // Verify that the pointed data is set to 42
    EXPECT_CALL(mymock, SetDataByPointer(Pointee(42)))
        .Times(1);

    /* Act */
    CheckSetDataByPointer(42);
}
