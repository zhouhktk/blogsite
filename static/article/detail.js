$(function () {
    editormd.markdownToHTML("article-body", {
        htmlDecode: "style,script,iframe",
        taskList: true,
        tex: true,
        emoji: true,
        flowChart: true,
        sequenceDiagram: true,
    });
});

// 判断提交的表单是否为空
function notempty() {
    let content = $.trim(CKEDITOR.instances['id_body'].document.getBody().getText());
    if (content.length === 0) {
        layer.msg("评论内容不能为空！");
        CKEDITOR.instances['id_body'].setData("");
        return false;
    } else return true;
}

// 加载 modal
function load_modal(article_id, comment_id) {
    let modal_body = '#modal_body_' + comment_id;
    let modal_id = '#comment_' + comment_id;

    // 加载编辑器
    if ($(modal_body).children().length === 0) {
        let content = '<iframe src="/comment/post-comment/' +
            article_id + '/' + comment_id + '"' +
            ' frameborder="0" style="width: 100%; height: 100%;" id="iframe_' +
            comment_id + '"></iframe>';
        $(modal_body).append(content);
    }
    $(modal_id).modal('show');
}

//处理二级回复
// function post_reply_and_show_it(new_comment_id, article_id) {
//     let next_url = '/article/detail'+article_id;
//     // 刷新并定位到锚点
//     location.replace(next_url + "#comment_elem_" + new_comment_id);
// }


// 点赞功能主函数
function give_likes(url, id, likes) {
    // 取出 LocalStorage 中的数据
    let storage = window.localStorage;
    const storage_likes_data = storage.getItem("blog_likes");
    // 获取点赞的json数据
    let likes_json_data = JSON.parse(storage_likes_data);
    // 若数据不存在，则创建空字典
    if (!likes_json_data) {
        likes_json_data = {}
    }
    // 检查当前文章是否已点赞。是则 status = true
    const status = is_liked(likes_json_data, id);
    if (status) {
        layer.msg('已经赞过啦~');
        // 点过赞则立即退出函数
        return;
    } else {
        // 用 jQuery 找到点赞数量，并 +1
        $('span#likes_number').text(likes + 1).css('color', '#ff6767');
        layer.msg("点赞成功！");
    }
    // 用 ajax 向后端发送 post 请求
    $.post(
        url,
        {},// post 只是为了做 csrf 校验，因此数据为空
        function (result) {
            if (result === 'success') {
                // 尝试修改点赞数据
                try {
                    likes_json_data[id] = true;
                } catch (e) {
                    window.localStorage.clear();
                }
                // 将字典转换为字符串，以便存储到 LocalStorage
                const d = JSON.stringify(likes_json_data);
                // 尝试存储点赞数据到 LocalStorage
                try {
                    storage.setItem("blog_likes", d);
                } catch (e) {
                    // code 22 错误表示 LocalStorage 空间满了
                    if (e.code === 22) {
                        window.localStorage.clear();
                        storage.setItem("blog_likes", d);
                    }
                }
            } else {
                layer.msg("点赞失败！过会儿再试试吧~");
            }

        }
    );
};

// 判断是否已经点过赞
function is_liked(data, id) {
    // 尝试查询点赞状态
    try {
        if (id in data && data[id]) {
            return true;
        } else {
            return false;
        }
    } catch (e) {
        window.localStorage.clear();
        return false;
    }
}
