Title: 扩展 ST2 Verilog 插件的 snippet
Date: 2014-07-04 23:31
Category: Tools
Tags: Sublime Text, verilog
Slug: extend-verilog-snippet-in-st2
Author: Qian Gu
Summary: 给 Sublime Text 插件添加新的 snippet

ST2 常用的插件，比如括号匹配、智能补全、自动对齐、Tags、注释生成、Terminal、Build、Git 等插件就不再赘述了，说一下网上介绍的比较少，但我自己使用比较多的关于 Verilog 的插件。

可以通过 Package 下载到两个插件，`Verilog` 和`Verilog-Automatic`。第一个插件主要功能是支持 Verilog 的代码高亮和补全，第二个插件可以帮助我们自动生成模块例化、端口添加连接等功能。

其中，第一个插件的 snippet 并不太让人满意，在原 snippet 的基础上，我添加了一些我常用到的 snippet。

## always

因为插件作者只添加了异步高有效复位方式的 `always` 块，而我们同步和异步两种方式都可能会用到，所以，我添加同步复位的 Snippet

ST 2 的 Package 都存放在 `/home/.config/sublime-text-2/Packages` 目录下面，我们需要修改的就是这个目录下的 `Verilog/Snippets` 下的 `.tmSnippet` 文件。修改后的结果如下：

**always-async.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>content</key>
    	<string>always @(posedge clk or ${1:posedge} ${2:rst}) begin
    	if ($2) begin
    		// reset
    		$3
    	end
    	else if ($4) begin
    		$0
    	end
    end</string>
    	<key>name</key>
    	<string>always-async</string>
    	<key>scope</key>
    	<string>source.verilog</string>
    	<key>tabTrigger</key>
    	<string>always-async</string>
    	<key>uuid</key>
    	<string>026B3DA6-E1B4-4F09-B7B6-9485ADEF34DC</string>
    </dict>
    </plist>
    
**always-sync.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>content</key>
    	<string>always @(posedge clk) begin
    	if (${1:rst}) begin
    		// reset
    		$2
    	end
    	else begin
    		$0
    	end
    end</string>
    	<key>name</key>
    	<string>always-sync</string>
    	<key>scope</key>
    	<string>source.verilog</string>
    	<key>tabTrigger</key>
    	<string>always-sync</string>
    	<key>uuid</key>
    	<string>026B3DA6-E1B4-4F09-B7B6-9485ADEF34DC</string>
    </dict>
    </plist>
    
修改之后的结果如下图所示：

![always](/images/extend-verilog-snippet-in-st2/always.gif)

## if-else

原来的 if snippet 没有 else 分支，所以，添加了一个有 else 分支的 if 语句。

**if.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>content</key>
    	<string>if ($1) begin
    	$0
    end</string>
    	<key>name</key>
    	<string>if</string>
    	<key>scope</key>
    	<string>source.verilog</string>
    	<key>tabTrigger</key>
    	<string>if</string>
    	<key>uuid</key>
    	<string>1ADE2F84-DDB8-4878-8BFC-B7FC2F391C6C</string>
    </dict>
    </plist>
    
**if-else.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>content</key>
    	<string>if ($1) begin
    	$2
    end
    else begin
    	$0
    end</string>
    	<key>name</key>
    	<string>if-else</string>
    	<key>scope</key>
    	<string>source.verilog</string>
    	<key>tabTrigger</key>
    	<string>if-else</string>
    	<key>uuid</key>
    	<string>1ADE2F84-DDB8-4878-8BFC-B7FC2F391C6C</string>
    </dict>
    </plist>
    
修改后的结果如下图：

![if-else](/images/extend-verilog-snippet-in-st2/if-else.gif)

## parameter

原来是没有 parameter 的snippets 的，拷贝一份其他的 snippet，修改其中的一些设置，即可

**parameter.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>content</key>
    	<string>parameter	$1 = $2,
    			$3 = $0
    </string>
    	<key>name</key>
    	<string>parameter</string>
    	<key>scope</key>
    	<string>source.verilog</string>
    	<key>tabTrigger</key>
    	<string>parameter</string>
    	<key>uuid</key>
    	<string>1ADE2F84-DDB8-4878-8BFC-B7FC2F391C6C</string>
    </dict>
    </plist>

修改后的结果如下图所示：

![parameter](/images/extend-verilog-snippet-in-st2/parameter.gif)

## case

原来是没有 case 的 snippet，方法同上，可以修改出我们想要的 case snippet

**case.tmSnippet**

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/Prop    ertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>content</key>
        <string>case ($1)
        $2: begin
            $3
        end
        $4: begin
            $5
        end
        $6: begin
            $7
        end
        $8: begin
            $9
        end
        default: begin
            $10
        end
    endcase</string>
        <key>name</key>
        <string>case</string>
        <key>scope</key>
        <string>source.verilog</string>
        <key>tabTrigger</key>
        <string>case</string>
        <key>uuid</key>
        <string>026B3DA6-E1B4-4F09-B7B6-9485ADEF34DC</string>
    </dict>
    </plist>
    
修改后的效果如下：

![case](/images/extend-verilog-snippet-in-st2/case.gif)