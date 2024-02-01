package main

import (
	"errors"
	"fmt"
	"github.com/deadblue/elevengo"
	"github.com/manifoldco/promptui"
	gim "github.com/ozankasikci/go-image-merge"
	"image/jpeg"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"runtime"
	"strconv"
)

var client *elevengo.Client

func init() {
	client = elevengo.Default()
}

func main() {
	// 创建一个新的 ServeMux
	mux := http.NewServeMux()

	// 添加您的路由处理函数
	mux.HandleFunc("/add-magnet-to-115", addUrl)
	mux.HandleFunc("/115-cookies", syncCookies)

	// 使用 CORS 中间件包装 ServeMux
	handlerWithCORS := enableCORS(mux)

	// 启动服务器
	if err := http.ListenAndServe(":3333", handlerWithCORS); err != nil {
		log.Fatalf("服务启动失败: %v", err)
	}
}

func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 设置允许的源，这里设置为允许所有源
		w.Header().Set("Access-Control-Allow-Origin", "*")

		// 设置允许的 HTTP 方法
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")

		// 设置允许的头信息
		w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

		// 预检请求使用 OPTIONS 方法，这里我们直接返回 200
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// 调用下一个处理器
		next.ServeHTTP(w, r)
	})
}

func syncCookies(writer http.ResponseWriter, request *http.Request) {
	if err := request.ParseForm(); err != nil {
		http.Error(writer, err.Error(), http.StatusBadRequest)
		return
	}

	cookies := request.FormValue("cookies")
	uidReg := regexp.MustCompile(`UID=(\w+);`)
	cidReg := regexp.MustCompile(`CID=(\w+);`)
	seidReg := regexp.MustCompile(`SEID=(\w+);`)
	uid := uidReg.FindAllStringSubmatch(cookies, -1)[0][1]
	cid := cidReg.FindAllStringSubmatch(cookies, -1)[0][1]
	seid := seidReg.FindAllStringSubmatch(cookies, -1)[0][1]

	_ = client.ImportCredentials(&elevengo.Credentials{
		UID:  uid,
		CID:  cid,
		SEID: seid,
	})

	fmt.Fprintf(writer, "同步成功")
	fmt.Printf("同步成功\n")
}

func addUrl(writer http.ResponseWriter, request *http.Request) {
	if err := request.ParseForm(); err != nil {
		http.Error(writer, err.Error(), http.StatusBadRequest)
		return
	}

	url := request.FormValue("param1")
	hash, err := client.OfflineAddUrl(url)
	if err != nil {
		if err.Error() == "请验证账号" {
			var captchaSession *elevengo.CaptchaSession
			captchaSession, err = client.CaptchaStart()

			expectImg := "115_captcha_expect.png"
			choicesImg := "115_captcha_choices.jpg"
			mergeImg := "115_captcha.jpg"
			defer os.Remove(expectImg)
			defer os.Remove(choicesImg)
			defer os.Remove(mergeImg)

			ioutil.WriteFile(expectImg, captchaSession.CodeValue, 0644)
			ioutil.WriteFile(choicesImg, captchaSession.CodeKeys, 0644)

			grids := []*gim.Grid{
				{ImageFilePath: expectImg},
				{ImageFilePath: choicesImg},
			}
			rgba, _ := gim.New(grids, 1, 2, gim.OptGridSize(255, 100)).Merge()
			file, _ := os.Create(mergeImg)
			err = jpeg.Encode(file, rgba, &jpeg.Options{Quality: 80})
			file.Close()

			openUrl(mergeImg)

			for {
				captcha, err := askCaptcha()
				if err != nil {
					fmt.Println(err)
				}

				if err := client.CaptchaSubmit(captcha, captchaSession); err != nil {
					fmt.Println(err)
					if err.Error() != "captcha code incorrect" {
						break
					}
				}

				break
			}
		}

		if err != nil {
			fmt.Println(err.Error())
			http.Error(writer, err.Error(), http.StatusBadRequest)
		} else {
			http.Error(writer, "添加失败", http.StatusBadRequest)
		}

		return
	}

	fmt.Fprintf(writer, "离线任务添加成功：%s", hash)
	fmt.Printf("离线任务添加成功：%s\n", hash)
}

func openUrl(url string) error {
	var cmd string
	var args []string

	switch runtime.GOOS {
	case "windows":
		cmd = "cmd"
		args = []string{"/c", "start"}
	case "darwin":
		cmd = "open"
	default: // "linux", "freebsd", "openbsd", "netbsd"
		cmd = "xdg-open"
	}
	args = append(args, url)
	c := exec.Command(cmd, args...)
	//c.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
	return c.Start()
}

func askCaptcha() (string, error) {
	validate := func(input string) error {
		_, err := strconv.ParseInt(input, 10, 16)
		if err != nil {
			return errors.New("输入 0-9 范围内的 4 个数字")
		}
		return nil
	}

	prompt := promptui.Prompt{
		Label:    "验证码(4位数，第一行0-4, 第二行5-9)",
		Validate: validate,
	}

	return prompt.Run()
}
