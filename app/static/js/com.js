//默认是用户管理
    document.addEventListener('DOMContentLoaded', function () {
        var defaultSection = document.getElementById('user');
        defaultSection.style.display = 'block';
    });
    //菜单切换的实现
    const menuLinks = document.querySelectorAll('.sidebar a');
    menuLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            const sections = document.querySelectorAll('section');
            sections.forEach(function (section) {
                section.style.display = 'none';
            });
            targetSection.style.display = 'block';
        });
    });

    //检测是否选择文件再导入
    function validateForm() {
        const fileInput = document.getElementById('file');
        if (fileInput.value == '') {
            alert('请先选择文件！');
            return false;
        }
        return true;
    }
