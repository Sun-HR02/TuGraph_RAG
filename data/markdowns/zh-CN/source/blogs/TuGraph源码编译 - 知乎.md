# TuGraph源码编译

## 简介

TuGraph 9月1号正式开源，提供docker镜像部署和源码编译部署两种方式。  
docker部署方式比较简单，在此略过。  

我们直接在tugraph-db目录下执行下面四步，如果成功则皆大欢喜，不过一般而言都会失败

> ./deps/build\_deps.sh  
> mkdir build  
> cd build  
> cmake ..  
> make -j8  
> make install

ARM环境下顺利编译对TuGraph需要做的修改点大致如下：

```text
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   CMakeLists.txt
        new file:   deps/incubator-brpc
        new file:   deps/jwt-cpp
        new file:   deps/prometheus-cpp
        new file:   deps/pybind11
        modified:   src/BuildCypherLib.cmake
        modified:   src/BuildPyClient.cmake
        modified:   src/BuildPythonPackage.cmake
        modified:   src/cmake/GenerateVersionInfo.cmake
        modified:   src/restful/server/json_convert.h
        modified:   src/restful/server/rest_server.cpp
        modified:   test/test_sync_file_implementations.cpp

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
  (commit or discard the untracked or modified content in submodules)
        modified:   deps/fma-common (modified content)
        modified:   deps/incubator-brpc (modified content, untracked content)
        modified:   deps/pybind11 (modified content)
        modified:   deps/tugraph-web (modified content)
```

## 依赖包安装

依赖包在Options.cmake可以找到，有一部分使用brew可以直接安装到系统的，另一部分下载源码安装到deps下

### 安装openmp到系统目录

```text
 curl -O https://mac.r-project.org/openmp/openmp-13.0.0-darwin21-Release.tar.gz 
  sudo tar fvxz openmp-13.0.0-darwin21-Release.tar.gz -C /
  clang++ -Xclang -fopenmp -lomp test.cpp -o test
```

### 安装boost库

```
 brew install boost
```



### 配置Java环境

```text
## 使用brew install java安装最新版本java

## 配置~/.bash_profile
export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home
export JAVA_INCLUDE_PATH=/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home/include

## 加载环境变量
source ~/.bash_profile
```

### 配置python 环境：

```text
将部分CMakeList.txt中的
find_package(PythonLibs 3 REQUIRED) 
统一改为 
find_package(Python3 REQUIRED)
  

安装最新的python
brew install python重新安装最新的python，并使用最新的版本。

如果还有问题，可以手动加载配置参数：
cmake . \
   -DPYTHON_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")  \
   -DPYTHON_LIBRARY=$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))") \
   -DPYTHON_EXECUTABLE:FILEPATH=`which python`

或者把PYTHON_INCLUDE_DIR、PYTHON_LIBRARY添加到.bash_profile中
```

### 安装jwt-cpp\[deps/下\]

```text
 下载到deps目录:
 https://github.com/Thalhammer/jwt-cpp
```

### 安装leveldb

```
brew install leveldb
```

### 安装protobuf

``` 
brew install protobuf
```

### 安装pybind11\[deps/下\]

```text
1. 源码安装
    git clone https://github.com/pybind/pybind11
    然后编译安装：

    mkdir build
    cd build
    cmake ..

    #check验证，提示-lpython3.8，比较诡异，后续重装python3.10才解决， check才跑通
    make check -j 4
    make install

    2. brew install pybind11 
    https://formulae.brew.sh/formula/pybind11


    3. 但是编译lgraph_python.dylib时，一直提示no modulor named: arm64
      
      需要修改BuildPythonPackage.cmake文件添加下面内容：
      if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
          set(CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS "${CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS} -undefined dynamic_lookup")
      endif()
```

### 安装cpptest

```text
https://github.com/microsoft/cpprestsdk
  brew install cpprestsdk
```

### 安装brpc\[deps/下\]

```text
https://github.com/apache/incubator-brpc
按照说明安装在deps目录下
sh -x ./config_brpc.sh --headers=/opt/homebrew/include --libs=/opt/homebrew/lib --cc=clang --cxx=clang++
make -j32
```

### 安装prometheus cpp库\[/deps目录下\]

```text
https://github.com/jupp0r/prometheus-cpp

# fetch third-party dependencies
git submodule init
git submodule update

mkdir _build
cd _build

# run cmake
cmake .. -DBUILD_SHARED_LIBS=ON -DENABLE_PUSH=OFF -DENABLE_COMPRESSION=OFF

# build
cmake --build . --parallel 4

# run tests
ctest -V

# install the libraries and headers
cmake --install .
```

## make失败

### cmake file修改

```text
## header 找不到、lib找不到； 修改CMakeLists.txt, 添加include和lib搜索目录
include_directories(SYSTEM /opt/homebrew/Cellar/boost/1.79.0_1/include/)
include_directories(SYSTEM /opt/homebrew/Cellar/protobuf/21.5/include/)
include_directories(SYSTEM ${path}/tugraph-db/deps/jwt-cpp/include/)
include_directories(SYSTEM ${path}/tugraph-db/deps/incubator-brpc/output/include/)
include_directories(SYSTEM /opt/homebrew/Cellar/cpprestsdk/2.10.18/include/)
include_directories(SYSTEM /opt/homebrew/Cellar/gflags//2.2.2/include/)
include_directories(SYSTEM /opt/homebrew/Cellar/googletest/1.12.1/include/)
include_directories(SYSTEM /opt/homebrew/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/include/python3.10)

link_directories(/opt/homebrew/Cellar/boost/1.79.0_1/lib/)
link_directories(/opt/homebrew/Cellar/protobuf/21.5/lib/)
link_directories(/opt/homebrew/Cellar/gflags/2.2.2/lib/)
link_directories(${path}/tugraph-db/deps/incubator-brpc/output/lib/)
link_directories(/opt/homebrew/Cellar/cpprestsdk/2.10.18/lib/)
link_directories(/opt/homebrew/Cellar/gperftools/2.10/lib)
link_directories(/opt/homebrew/Cellar/snappy/1.1.9/lib/)
link_directories(/opt/homebrew/Cellar/googletest/1.12.1/lib/)
link_directories(/opt/homebrew/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/lib)


## src/BuildCypherLib.cmake
find_package(PythonLibs REQUIRED) => find_package(Python3 REQUIRED)

## src/BuildPyClient.cmake
find_package(PythonLibs REQUIRED) => find_package(Python3 REQUIRED)

## src/cmake/GenerateVersionInfo.cmake
find_package(PythonLibs 3 REQUIRED) => find_package(Python3 REQUIRED)

## src/BuildPythonPackage.cmake
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
    set(CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS "${CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS} -undefined dynamic_lookup")
endif()
```



### 修改src/restful/server/json\_convert.h

```c
git diff  src/restful/server/json_convert.h  src/restful/server/json_convert.h

diff --git a/src/restful/server/json_convert.h b/src/restful/server/json_convert.h
index 1f705ba..cdb868a 100644
--- a/src/restful/server/json_convert.h
+++ b/src/restful/server/json_convert.h
@@ -366,22 +366,22 @@ inline web::json::value ValueToJson(const TaskTracker::Stats& stats) {
     ret[_TU("requests/second")] = web::json::value::number(stats.qps);
     ret[_TU("writes/second")] = web::json::value::number(stats.tps);
     ret[_TU("failure_rate")] = web::json::value::number(stats.failure_rate);
-    ret[_TU("running_tasks")] = web::json::value::number(stats.n_running);
+    ret[_TU("running_tasks")] = web::json::value::number((uint32_t)stats.n_running);
     return ret;
 }
 
 inline web::json::value ValueToJson(const fma_common::HardwareInfo::CPURate& cpuRate) {
     web::json::value js_cpu;
-    js_cpu[_TU("self")] = web::json::value::number((size_t)cpuRate.selfCPURate);
-    js_cpu[_TU("server")] = web::json::value::number((size_t)cpuRate.serverCPURate);
+    js_cpu[_TU("self")] = web::json::value::number(cpuRate.selfCPURate);
+    js_cpu[_TU("server")] = web::json::value::number(cpuRate.serverCPURate);
     js_cpu[_TU("unit")] = web::json::value::string(_TU("%"));
     return js_cpu;
 }
 
 inline web::json::value ValueToJson(const fma_common::HardwareInfo::DiskRate& diskRate) {
     web::json::value js_disk;
-    js_disk[_TU("read")] = web::json::value::number((size_t)diskRate.readRate);
-    js_disk[_TU("write")] = web::json::value::number((size_t)diskRate.writeRate);
+    js_disk[_TU("read")] = web::json::value::number(diskRate.readRate);
+    js_disk[_TU("write")] = web::json::value::number(diskRate.writeRate);
     js_disk[_TU("unit")] = web::json::value::string(_TU("B/s"));
     return js_disk;
 }
@@ -399,7 +399,7 @@ inline web::json::value ValueToJson(const fma_common::DiskInfo& diskInfo, size_t
     web::json::value js_space;
     js_space[_TU("total")] = web::json::value::number((uint64_t)diskInfo.total);
     js_space[_TU("available")] = web::json::value::number((uint64_t)diskInfo.avail);
-    js_space[_TU("self")] = web::json::value::number(graph_used);
+    js_space[_TU("self")] = web::json::value::number((uint32_t)graph_used);
     js_space[_TU("unit")] = web::json::value::string(_TU("B"));
     return js_space;
 }
@@ -413,7 +413,7 @@ inline web::json::value ValueToJson(const std::pair<std::string, std::string>& p
 
 inline web::json::value ValueToJson(const DBConfig& conf) {
     web::json::value ret;
-    ret[RestStrings::MAX_SIZE_GB] = conf.db_size / 1024 / 1024 / 1024;
+    ret[RestStrings::MAX_SIZE_GB] = web::json::value::number((double)(conf.db_size / 1024 / 1024 / 1024));
     ret[RestStrings::DESC] = ValueToJson(conf.desc);
     return ret;
 }
@@ -554,7 +554,7 @@ inline web::json::value ValueToJson(const AclManager::UserInfo& info) {
     js[RestStrings::ROLES] = ValueToJson(info.roles);
     js[RestStrings::AUTH_METHOD] = ValueToJson(info.auth_method);
     js[RestStrings::DESC] = web::json::value(_TU(info.desc));
-    js[RestStrings::MEM_LIMIT] = web::json::value(info.memory_limit);
+    js[RestStrings::MEM_LIMIT] = web::json::value((uint32_t)info.memory_limit);
     return js;
 }
```

### 修改src/restful/server/rest\_server.cpp

```text
diff --git a/src/restful/server/rest_server.cpp b/src/restful/server/rest_server.cpp
index 0b0aff1..14b0214 100644
--- a/src/restful/server/rest_server.cpp
+++ b/src/restful/server/rest_server.cpp
@@ -900,8 +900,8 @@ bool RestServer::RedirectIfServerTooOld(const http_request& request,
 static web::json::value GetCPURate() {
     fma_common::HardwareInfo::CPURate cpuRate = fma_common::HardwareInfo::GetCPURate();
     web::json::value js_cpu;
-    js_cpu[_TU("self")] = web::json::value::number((size_t)cpuRate.selfCPURate);
-    js_cpu[_TU("server")] = web::json::value::number((size_t)cpuRate.serverCPURate);
+    js_cpu[_TU("self")] = web::json::value::number(cpuRate.selfCPURate);
+    js_cpu[_TU("server")] = web::json::value::number(cpuRate.serverCPURate);
     js_cpu[_TU("unit")] = web::json::value::string(_TU("%"));
     return js_cpu;
 }
@@ -909,8 +909,8 @@ static web::json::value GetCPURate() {
 static web::json::value GetDiskRate() {
     fma_common::HardwareInfo::DiskRate diskRate = fma_common::HardwareInfo::GetDiskRate();
     web::json::value js_disk;
-    js_disk[_TU("read")] = web::json::value::number((size_t)diskRate.readRate);
-    js_disk[_TU("write")] = web::json::value::number((size_t)diskRate.writeRate);
+    js_disk[_TU("read")] = web::json::value::number(diskRate.readRate);
+    js_disk[_TU("write")] = web::json::value::number(diskRate.writeRate);
     js_disk[_TU("unit")] = web::json::value::string(_TU("B/s"));
     return js_disk;
 }
@@ -933,7 +933,7 @@ static web::json::value GetDbSpace(const std::string& dir) {
     struct fma_common::DiskInfo diskInfo;
     fma_common::GetDiskInfo(diskInfo, dir.c_str());
     web::json::value js_space;
-    js_space[_TU("space")] = web::json::value::number(dbSpace);
+    js_space[_TU("space")] = web::json::value::number((uint64_t)dbSpace);
     js_space[_TU("disk_total")] = web::json::value::number((uint64_t)diskInfo.total);
     js_space[_TU("disk_avail")] = web::json::value::number((uint64_t)diskInfo.avail);
     js_space[_TU("unit")] = web::json::value::string(_TU("B"));
@@ -1130,8 +1130,8 @@ void RestServer::HandleGetNode(const std::string& user, AccessControlledDB& db,
     if (paths.size() == 3) {  // summary of node
         auto txn = db.CreateReadTxn();
         auto n1 = txn.GetNumLabels(true);
-        response[RestStrings::NUM_LABELS] = web::json::value::number(n1);
-        response[RestStrings::NUMV] = web::json::value::number(txn.GetLooseNumVertex());
+        response[RestStrings::NUM_LABELS] = web::json::value::number((uint64_t)n1);
+        response[RestStrings::NUMV] = web::json::value::number((uint64_t)txn.GetLooseNumVertex());
         return RespondSuccess(request, response);
     }
     lgraph::VertexId id;
@@ -1214,7 +1214,7 @@ void RestServer::HandleGetRelationship(const std::string& user, AccessControlled
     if (paths.size() == 3) {
         auto txn = db.CreateReadTxn();
         auto n2 = txn.GetNumLabels(false);
-        response[RestStrings::NUM_LABELS] = web::json::value::number(n2);
+        response[RestStrings::NUM_LABELS] = web::json::value::number((uint64_t)n2);
         return RespondSuccess(request, response);
     }
     // /relationship/uid/...
@@ -1632,7 +1632,7 @@ void RestServer::HandlePostCypher(const std::string& user, const std::string& to
             }
             response[RestStrings::HEADER] = web::json::value::array(vec_header);
             response[RestStrings::RESULT] = web::json::value::array(vec_result);
-            response[RestStrings::SZ] = web::json::value::number(vec_result.size());
+            response[RestStrings::SZ] = web::json::value::number((uint32_t)vec_result.size());
             response[RestStrings::ELAPSED] =
                 web::json::value::number(resp.binary_result().elapsed());
             return RespondSuccess(request, response);
```

### 修改test/test\_sync\_file\_implementations.cpp

```text
diff --git a/test/test_sync_file_implementations.cpp b/test/test_sync_file_implementations.cpp
index b066c36..7fc8c6c 100644
--- a/test/test_sync_file_implementations.cpp
+++ b/test/test_sync_file_implementations.cpp
@@ -5,7 +5,7 @@
 #include <fcntl.h>
 
 #include <fstream>
-
+#include <unistd.h>
 #include "gtest/gtest.h"
 #include "fma-common/configuration.h"
 #include "fma-common/file_system.h"
@@ -150,7 +150,7 @@ TEST_F(TestSyncFileImpl, FDataSync) {
                 written_bytes += write(file, write_buf_.data(), write_buf_.size());
             }
             // commit
-            fdatasync(file);
+            fsync(file);
         }
         EndOneTest();
         t1 = fma_common::GetTime();
```

## make install

```text
提示缺少部分目录创建目录, 需要自行创建 mkdir -p /xxx/tugraph-db/src/restful/server/resource
```

## 编译tugraph-web

需要export NODE\_OPTIONS=--openssl-legacy-provider，否则会报

```c
Error: error:0308010C:digital envelope routines::unsupported at new Hash (node:internal/crypto/hash:71:19) at Object.createHash (node:crypto:133:10) at ${path}/deps/tugraph-web/node_modules/terser-webpack-plugin/dist/index.js:217:37
```

等类似错误
