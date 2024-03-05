package main

import (
	"fmt"
	"os"
	"path/filepath"
)

func main() {
	// 定义文件夹路径
	const path = "../../client"

	// 构建文件夹的绝对路径
	absPath, err := filepath.Abs(path)
	if err != nil {
		fmt.Println("无法获取文件夹路径：", err)
		return
	}

	// 打开文件夹
	dir, err := os.Open(absPath)
	if err != nil {
		fmt.Println("无法打开文件夹：", err)
		return
	}
	defer dir.Close()

	// 读取文件夹中的所有文件名
	fileNames, err := dir.Readdirnames(-1)
	if err != nil {
		fmt.Println("无法读取文件夹内容：", err)
		return
	}

	// 打印文件名列表
	fmt.Println("文件夹", absPath, "中的文件列表：")
	for _, name := range fileNames {
		fmt.Println(name)
	}
}
