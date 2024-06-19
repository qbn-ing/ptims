$(document).ready(function () {
        //用户管理
        $('.confirm').hide();
        $('.cancel').hide();
        // 绑定删除按钮的点击事件
        $(".delete").click(function (event) {
            event.preventDefault();
            var deleteForm = $(this).closest(".delete-form");
            // 判断要删除的用户是否为当前登录用户
            if (deleteForm.closest('tr').data('name') == '{{ username }}') {
                alert('不能删除当前登录用户');
            } else {
                // 弹出确认删除对话框
                if (confirm("确定要删除吗？")) {
                    // 发送AJAX请求到后端路由
                    $.ajax({
                        type: deleteForm.attr("method"),
                        url: deleteForm.attr("action"),
                        data: deleteForm.serialize(),
                        success: function (response) {
                            // 弹出删除成功提示框
                            alert("删除成功");
                            // 刷新网页
                            location.reload();
                        },
                        error: function (error) {
                            console.log(error);
                        }
                    });
                }
            }
        });
        //绑定编辑按钮的点击事件

        $('.edit').on('click', function (e) {
            e.preventDefault();
            const row = $(this).closest('tr');
            const name = row.find('td:eq(0)');
            const password = row.find('td:eq(1)');
            const email = row.find('td:eq(2)');
            const state = row.find('td:eq(3)');
            const actions = row.find('td:eq(4)');
            const Form = $(this).closest(".update-form");
            Form.closest('tr').data('id')
            name.html(`<input type="text" value="${name.text()}">`);
            password.html(`<input type="password" value="${password.text()}">`);
            email.html(`<input type="text" value="${email.text()}">`);
            state.html(`
            <select>
                <option value="启用" ${state.text() === '启用' ? 'selected' : ''}>启用</option>
                <option value="停用" ${state.text() === '停用' ? 'selected' : ''}>停用</option>
            </select>
        `);
            actions.find('.edit').css('display', 'none');
            actions.find('.delete').css('display', 'none');
            actions.find('.confirm').css('display', 'inline');
            actions.find('.cancel').css('display', 'inline');
        });
        $('.confirm').on('click', function (e) {
            e.preventDefault();
            const row = $(this).closest('tr');
            const id = row.data('id');
            const name = row.find('td:eq(0) input').val();
            const password = row.find('td:eq(1) input').val();
            const email = row.find('td:eq(2) input').val();
            const state = row.find('td:eq(3) select').val();

            $.ajax({
                url: '/profile',
                method: 'POST',
                data: {
                    'id': id,
                    'name': name,
                    'password': password,
                    'email': email,
                    'state': state
                },
                success: function (response) {
                    if (response.result == 'success') {
                        alert("更新成功");
                        location.reload();
                    } else {
                        alert("更新失败:" + response.message);
                        console.log(response);
                    }
                },
                error: function (response) {
                    alert("更新失败" + response.responseText);
                    console.log(response);
                }
            });
        });

        $('.cancel').on('click', function (e) {
            e.preventDefault();
            location.reload();
        });
    })