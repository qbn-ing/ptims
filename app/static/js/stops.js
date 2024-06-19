$(document).ready(function () {

        //公交站的删除操作
    $('.confirms').hide();
    $('.cancels').hide();
    // 绑定删除按钮的点击事件
    $(".deletes").click(function (event) {
        event.preventDefault();
        const deleteForm = $(this).closest(".delete-forms");
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
                    alert(error)
                    console.log(error);
                }
            });
        }

    });
    //绑定编辑按钮的点击事件

    $('.edits').on('click', function (e) {
        e.preventDefault();
        const row = $(this).closest('tr');
        const name = row.find('td:eq(1)');
        const location1 = row.find('td:eq(2)');
        const location2 = row.find('td:eq(3)');
        const state = row.find('td:eq(4)');
        const actions = row.find('td:eq(5)');
        const Form = $(this).closest(".update-forms");
        Form.closest('tr').data('id')
        name.html(`<input type="text" value="${name.text()}">`);
        location1.html(`<input type="text" value="${location1.text()}">`);
        location2.html(`<input type="text" value="${location2.text()}">`);
        state.html(`
            <select>
                <option value="启用" ${state.text() === '正常' ? 'selected' : ''}>正常</option>
                <option value="停用" ${state.text() === '停用' ? 'selected' : ''}>停用</option>
            </select>
        `);
        actions.find('.edits').css('display', 'none');
        actions.find('.deletes').css('display', 'none');
        actions.find('.confirms').css('display', 'inline');
        actions.find('.cancels').css('display', 'inline');
    });
    $('.confirms').on('click', function (e) {
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