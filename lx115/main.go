package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"runtime"

	"github.com/deadblue/elevengo"
	"github.com/manifoldco/promptui"
	gim "github.com/ozankasikci/go-image-merge"
	"image/jpeg"
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
		log.Printf("解析表单失败: %v\n", err)
		http.Error(writer, err.Error(), http.StatusBadRequest)
		return
	}

	cookies := request.FormValue("cookies")
	if cookies == "" {
		log.Println("未收到cookies数据")
		http.Error(writer, "cookies数据为空", http.StatusBadRequest)
		return
	}

	log.Printf("收到cookies数据，长度: %d\n", len(cookies))

	// 使用更精确的正则表达式
	uidReg := regexp.MustCompile(`UID=([^;]+)`)
	cidReg := regexp.MustCompile(`CID=([^;]+)`)
	seidReg := regexp.MustCompile(`SEID=([^;]+)`)

	uidMatches := uidReg.FindStringSubmatch(cookies)
	cidMatches := cidReg.FindStringSubmatch(cookies)
	seidMatches := seidReg.FindStringSubmatch(cookies)

	if len(uidMatches) < 2 || len(cidMatches) < 2 || len(seidMatches) < 2 {
		log.Printf("无法解析cookies数据: UID=%v, CID=%v, SEID=%v\n", 
			len(uidMatches) > 1, len(cidMatches) > 1, len(seidMatches) > 1)
		http.Error(writer, "cookies格式错误或缺少必要数据", http.StatusBadRequest)
		return
	}

	uid := uidMatches[1]
	cid := cidMatches[1]
	seid := seidMatches[1]

	log.Printf("解析结果 - UID: %s, CID: %s, SEID: %s\n", uid, cid, seid)

	if err := client.ImportCredentials(&elevengo.Credentials{
		UID:  uid,
		CID:  cid,
		SEID: seid,
	}); err != nil {
		log.Printf("导入凭据失败: %v\n", err)
		http.Error(writer, fmt.Sprintf("导入凭据失败: %v", err), http.StatusInternalServerError)
		return
	}

	writer.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(writer, `{"status": "success", "message": "同步成功"}`)
	log.Println("同步成功")
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
				fmt.Println("captcha: ", captcha)
				if err != nil {
					fmt.Println(err)
				} else if err := client.CaptchaSubmit(captcha, captchaSession); err != nil {
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
		if len(input) != 4 {
			return errors.New("验证码必须是4位数字")
		}
		for _, c := range input {
			if c < '0' || c > '9' {
				return errors.New("请输入0-9范围内的数字")
			}
		}
		return nil
	}

	prompt := &promptui.Prompt{
		Label:    "请输入验证码(4位数字)",
		Validate: validate,
		Default:  "",
	}

	for {
		result, err := prompt.Run()
		if err == nil {
			return result, nil
		}
		if err == promptui.ErrInterrupt {
			return "", err
		}
		fmt.Printf("输入错误: %v\n请重新输入验证码\n", err)
	}
}
