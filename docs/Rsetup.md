#macOS 

~/.R/Makevars

XC_LOC:=$(shell xcrun --show-sdk-path)
LLVM_LOC:=$(shell brew --prefix llvm)
GCC_LOC:=$(shell brew --prefix gcc)
GETTEXT_LOC:=$(shell brew --prefix gettext)
OMP_LOC:=$(shell brew --prefix libomp)

CC=$(LLVM_LOC)/bin/clang
CXX=$(LLVM_LOC)/bin/clang++
CXX11=$(LLVM_LOC)/bin/clang++
CXX14=$(LLVM_LOC)/bin/clang++
CXX17=$(LLVM_LOC)/bin/clang++
CXX1X=$(LLVM_LOC)/bin/clang++

CFLAGS=-g -O2 -Wall -pedantic -std=gnu99 -mtune=native -pipe
CXXFLAGS=-g -O2 -Wall -pedantic -std=c++11 -mtune=native -pipe
LDFLAGS=-L"$(LLVM_LOC)/lib" -L"$(GETTEXT_LOC)/lib" -Wl,-rpath,$(LLVM_LOC)/lib --sysroot="$(XC_LOC)" -lomp
CPPFLAGS=-I"$(GETTEXT_LOC)/include" -I"$(LLVM_LOC)/include" -I"$(OMP_LOC)/include" -isysroot "$(XC_LOC)" -Xclang -fopenmp

FC=$(GCC_LOC)/bin/gfortran
F77=$(GCC_LOC)/bin/gfortran
FLIBS=-L$(GCC_LOC)/lib/gcc/10/ -lm
