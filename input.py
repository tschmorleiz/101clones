from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'companies101.views.home', name='home'),
    # url(r'^companies101/', include('companies101.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'company.views.index'),
    url(r'^company/department/(?P<department_name>[a-zA-Z0-9_\.]+)', 'company.views.department'),
    url(r'^company/employee/(?P<employee_name>[a-zA-Z0-9_\.]+)', 'company.views.employee'),
    url(r'^company/cut', 'company.views.cut'),
    url(r'^company/total', 'company.views.total')
)
