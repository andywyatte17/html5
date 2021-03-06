cmake_minimum_required(VERSION 3.0.2)

set (LIBNAME A)

project(${LIBNAME})

macro(install_libs)
  FILE(TO_CMAKE_PATH "${CMAKE_CURRENT_BINARY_DIR}/install/" INSTALL_DST_DIR_TMP)
  if(CMAKE_CL_64)
    INSTALL(TARGETS ${LIBNAME}
      ARCHIVE DESTINATION "${INSTALL_DST_DIR_TMP}/libs"
      CONFIGURATIONS Debug;Release;RelWithDebInfo;MinSizeRel)
  else()
    INSTALL(TARGETS ${LIBNAME}
      ARCHIVE DESTINATION "${INSTALL_DST_DIR_TMP}/libs"
      CONFIGURATIONS Debug;Release;RelWithDebInfo;MinSizeRel)
  endif()
endmacro()

set(SOURCES_ROOT
  "./a.cpp"
  "./a.h"
  "./main.cpp"
)

set(SOURCES_RC
  "./a.rc"
  "./a.rc2"
)

set(SOURCES_F1
  "f1/a1.cpp"
)

source_group("_Src" FILES ${SOURCES_ROOT})

source_group("rc" FILES ${SOURCES_RC})

source_group("f1" FILES ${SOURCES_F1})



add_library(${LIBNAME} SHARED
${SOURCES_ROOT}
${SOURCES_RC}
${SOURCES_F1}
)

# INSTALL_DST_ROOT should be in CMAKE_PATH format - it then works correctly
#   with INSTALL(CODE "...")
FILE(TO_CMAKE_PATH "${CMAKE_CURRENT_BINARY_DIR}/install/" INSTALL_DST_ROOT)
SET(INSTALL_DST_ROOT "${INSTALL_DST_ROOT}/HeaderFiles/Dlls/${LIBBASE}")

# Clean-up header files folder
# install(CODE "FILE(REMOVE_RECURSE ${INSTALL_DST_ROOT})")

# Install header files

INSTALL(FILES
   "a.h" DESTINATION "${INSTALL_DST_ROOT}/A/")

# Give the output name something different to the Release
set_target_properties(${LIBNAME} PROPERTIES OUTPUT_NAME_DEBUG ${LIBNAME}D)
set_target_properties(${LIBNAME} PROPERTIES COMPILE_PDB_NAME_DEBUG ${LIBNAME}D)
set_target_properties(${LIBNAME} PROPERTIES COMPILE_PDB_NAME_RELEASE ${LIBNAME})
set_target_properties(${LIBNAME} PROPERTIES COMPILE_PDB_NAME_RELWITHDEBINFO ${LIBNAME})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAG} /EHsc /wd4456 /wd4458 /wd4459 /wd4457")

install_libs()
