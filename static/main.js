//处理标签
function rand_color(selector) {
    var colors = ['badge-primary', 'badge-success', 'badge-info', 'badge-secondary', 'badge-danger', 'badge-warning'];
    var badges = $(selector);
    for (let i = 0; i < badges.length; i++) {
        $(badges.get(i)).addClass(colors[i % 6]);
    }
}

rand_color('.tag-name');

// 悬浮在card上时添加阴影 让过渡效果持续 0.4 秒
$('.card').hover(function () {
    $(this).css({'box-shadow': '0px 1px 7px #8F8F8F', 'transition-duration': '0.3s'});
}, function () {
    $(this).css({'box-shadow': '', 'transition-duration': '0.3s'});
});
