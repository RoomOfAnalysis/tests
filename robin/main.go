package main

import (
	"flag"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

func rename_all_files_in_dir(dir string) {
	list, err := ioutil.ReadDir(dir)
	if err != nil {
		log.Fatalf("Failed to open directory: %s\n", err)
	}

	// sort
	sort.Slice(list, func(i, j int) bool {
		iName := list[i].Name()
		iName = iName[strings.LastIndex(iName, "-C") : len(iName)-4]
		jName := list[j].Name()
		jName = jName[strings.LastIndex(jName, "-C") : len(jName)-4]
		return iName < jName
	})

	firstName := list[0].Name()
	middleLeftIdx := strings.Index(firstName, "(")
	middleRightIdx := strings.Index(firstName, ")")
	if middleLeftIdx == -1 || middleRightIdx == -1 {
		log.Fatalf("Failed to parse the file name, no `()` found\n")
	}
	middleName := strings.TrimSpace(firstName[middleLeftIdx+1 : middleRightIdx])
	//log.Println("middleName", middleName)
	middleNameSpaceIdx := strings.Index(middleName, " ")
	siteName := middleName[:middleNameSpaceIdx]
	//log.Println("siteName", siteName)
	floorNumber := middleName[middleNameSpaceIdx+1 : strings.Index(middleName, "层")]
	//log.Println("floorNumber", floorNumber)
	if floorNumber == "首" {
		floorNumber = "一"
	}
	numStr := strings.Join(TakeChineseNumberFromString(floorNumber).(map[string]interface{})["digitsStringList"].([]string), "")
	num, err := strconv.Atoi(numStr)
	if err != nil {
		log.Fatalf("Failed to parse the file Chinese number: %s\n", floorNumber)
	}
	//log.Println("num", num)
	for _, file := range list {
		oldName := file.Name()
		idx := strings.Index(oldName, "-JS-")
		if idx == -1 {
			continue
		}
		newName := oldName[idx+1 : len(oldName)-4]
		numberStr := digitsToCHChars([]string{strconv.Itoa((num))})[0]
		if len(numberStr) > 3 {
			numberStr = numberStr[:3] + "十" + numberStr[3:]
			if numberStr[:3] == "一" {
				numberStr = numberStr[3:]
			}
		}
		//log.Println(numberStr)
		numberStr = strings.Replace(numberStr, "零", "", -1)

		newName += " ( " + siteName + " " + numberStr + "层平面图 ).pdf"
		err := os.Rename(filepath.Join(dir, oldName), filepath.Join(dir, newName))
		if err != nil {
			log.Printf("Error renaming file: %s with %s\n", oldName, newName)
		}
		num++
	}
}

var dirName = flag.String("-dir", "", "Directory Name")

func isFlagPassed(name string) bool {
	found := false
	flag.Visit(func(f *flag.Flag) {
		if f.Name == name {
			found = true
		}
	})
	return found
}

func init() {
	flag.StringVar(dirName, "-d", "", "Directory Name")
}

func main() {
	flag.Parse()
	if isFlagPassed(*dirName) {
		rename_all_files_in_dir(*dirName)
	} else if len(os.Args) > 1 {
		rename_all_files_in_dir(os.Args[1])
	} else {
		log.Fatalln("Please provide the directory name")
	}
}
