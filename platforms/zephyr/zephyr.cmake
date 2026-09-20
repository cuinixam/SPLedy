# Included by the root CMakeLists.txt before project(), which is where Zephyr
# requires find_package(Zephyr): it sets up the toolchain, devicetree and Kconfig.
# Boards defined here (boards/<vendor>/<board>/) are found next to Zephyr's own.
list(APPEND BOARD_ROOT ${CMAKE_CURRENT_LIST_DIR})
find_package(Zephyr REQUIRED HINTS ${ZEPHYR_BASE})
