# TestPointGenerator 使用手册

## 简介

TestPointGenerator 是一个带图形界面的测试点生成工具，专为 OI 出题人设计。你可以通过鼠标点击添加多个变量，设置每个变量的类型和参数，然后一键生成多组测试数据。

---

## 下载与安装

### 方式一：下载 exe 文件（推荐，无需 Python 环境）
1. 访问本仓库的 [Releases](https://github.com/MoonGazing123/TestPointGenerator/releases) 页面。
2. 下载最新版本的 `TestPointGenerator.exe` 文件。
3. 双击运行即可。

### 方式二：从源码运行（需 Python 环境）
```bash
git clone https://github.com/MoonGazing123/TestPointGenerator.git
cd TestPointGenerator
pip install -r requirements.txt
python main.py
```

## 制作你的std.exe
`std.exe`是你题目的标准程序（可以理解为题目的正解），用于生成测试数据。TPG 会调用它，把 .in 文件作为输入，然后自动生成对应的 .out。
### 第一步：准备你的C++代码
假设你有一道 A+B 题目，标准程序如下：
```cpp
#include<bits/stdc++.h>
using namespace std;
int main(){
  int a,b;
  cin>>a>>b;
  cout<<a+b<<"\n";
  return 0;
}
```
### 第二步：编译生成std.exe
#### 方法一：使用你的编译器（此处以VS Code为例）
1. 打开你的std.cpp文件
2. 运行一遍程序，如果你的VSCODE装载了Code Runner插件，运行时会自动编译出std.exe文件
3. 找到对应的可执行文件，使用TPG将其导入。
#### 方法二：使用命令行（g++）
1. 在 std.cpp 所在的文件夹打开终端（CMD 或 PowerShell）。
2. 执行以下命令：
```bash
g++ std.cpp -o std.exe
```
3. 如果提示`"g++"不是内部或外部命令`，说明你的电脑尚未安装C++编译器，需要先安装MinGW并配置环境变量
## 快速开始
### 第一步：选择`std.exe`
点击 「浏览」 按钮，选择你题目的标准程序（std.exe）。如果它已经在程序目录下，也可以直接跳过这一步。
### 第二步：添加变量
点击 「添加变量」，会在列表中新增一行。每个变量代表你测试数据中的一个字段。
### 第三步：配置变量
在变量列表中点击选中一个变量，右侧会出现详细的参数设置区，你可以配置：
- **变量名**:给变量起一个名字（如 n、a、pi）
- **数据类型**：整数、浮点数、字符串、字符、布尔值
- **参数**：不同类型有不同的参数（如整数的范围、字符串的长度和字符集）
### 第四步：修改或删除变量
- 选中变量后，在右侧修改参数，点击 「更新变量」 保存。
- 点击变量列表右侧的 「×」 按钮可以删除该变量。
### 第五步：设置生成组数
在顶部输入框中，输入你要生成的测试点数量（比如 10）。
### 第六步：生成
点击 「生成测试点」 按钮，等待生成完成。
> 生成完成后，当前目录会出现一个 test_data.zip 文件，里面包含了所有 .in 和 .out 文件。

## 反馈与建议
如果你在使用过程中遇到问题，或有改进建议，欢迎在本仓库的 [Issues](https://github.com/MoonGazing123/TestPointGenerator/issues)页面提出。
