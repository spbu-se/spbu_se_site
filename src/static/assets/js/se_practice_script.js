$(document).ready(function(){ UpdateReady(); });

function UpdateReady()
{
    //Practice student
    $('#index_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice', 'GET', null, 'Главная');
    });

    $('#guide_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice/guide', 'GET', null, 'Справочник');
    });

    $('#new_work_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice/new', 'GET', null, 'Новая работа');
    });

    $('#edit_topic_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice/edit_theme', 'GET', {id: this.name}, 'Выбор темы');
    });

    $('#new_report_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice/add_new_report', 'GET', {id: this.name}, 'Новый отчёт');
    });

    $('.nav').each(function()
    {
        let thesis_id = this.id;
        for (let button of this.children)
        {
            switch (button.name)
            {
                case 'choosing_topic_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/choosing_topic', 'GET', {id: thesis_id}, 'Выбор темы');
                    }
                    break;
                case 'goals_tasks_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/goals_tasks', 'GET', {id: thesis_id}, 'Цели и задачи');
                    }
                    break;
                case 'reports_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/workflow', 'GET', {id: thesis_id}, 'Отчётность');
                    }
                    break;
                case 'preparation_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/preparation_for_defense', 'GET', {id: thesis_id}, 'Подготовка к защите');
                    }
                    break;
                case 'defense_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/defense', 'GET', {id: thesis_id}, 'Защита');
                    }
                    break;
                case 'data_for_practice_button':
                    button.onclick = function(event)
                    {
                        event.preventDefault();
                        LoadPageWithAjax('/practice/data_for_practice', 'GET', {id: thesis_id}, 'Настройки');
                    }
                    break;
            }
        }
    });

    //Practice staff
    $('#current_thesises_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice_staff', 'GET', null, 'Текущие работы');
    });

    $('#finished_thesises_button').click( function(event)
    {
        event.preventDefault();
        LoadPageWithAjax('/practice_staff/finished_thesises', 'GET', null, 'Завершённые работы');
    });

    $("a[name='thesis_link']").each(function()
    {
        $(this).click(function(event)
        {
            event.preventDefault();
            LoadPageWithAjax('/practice_staff/thesis', 'GET', {id: this.id}, 'Текущие работы');
        });
    });

    $("a[name='reports_link']").each(function()
    {
        $(this).click(function(event)
        {
            event.preventDefault();
            LoadPageWithAjax('/practice_staff/reports', 'GET', {id: this.id}, 'Отчёты');
        });
    });

    $("input[type='file']").each(function()
    {
        $(this).on('change',function()
        {
            var fileName = $(this).val();
            fileName = fileName.replace("C:\\fakepath\\", "");
            $(this).next('label').html(fileName);
        });
    });

    window.onpopstate = function(e)
    {
        if(e.state)
        {
            $("#content").html(e.state.html);
            document.title = e.state.pageTitle;
            UpdateReady();
            feather.replace();
        }
        else
        {
            location.reload();
        }
    };

    let practice_filter_element = document.getElementById('guide_button');
    if (practice_filter_element){
        $('[data-toggle="popoverhover"]').popover({ trigger: "hover" });
    }
}

function LoadPageWithAjax(url, typeRequest, dataForRequest, title)
{
    req = $.ajax(
    {
        url: url,
        type: typeRequest,
        data: dataForRequest
    });
    req.done(function(response)
    {
        $('#content').html(response);
        document.title = title;
        let fullUrl = url;
        if (dataForRequest)
        {
            fullUrl += '?';
            for (let parametr in dataForRequest)
            {
                if (fullUrl[fullUrl.length - 1] != '?')
                {
                    fullUrl += '&';
                }
                fullUrl += parametr + '=' + dataForRequest[parametr];
            }
        }
        window.history.pushState({"html":$("#content").html(),"pageTitle":document.title},'', fullUrl);
        UpdateReady();
        feather.replace();
    });

}
