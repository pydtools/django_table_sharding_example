import pprint

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.base import model_sharding


class User(models.Model, model_sharding.ShardingMixin):
    user_name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    age = models.IntegerField(default=18)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Constant-based sharding
    SHARDING_TYPE = 'precise'
    SHARDING_COUNT = 10

    def __str__(self):
        return "%s:%s" % (str(self.id), self.name)

    class Meta:
        abstract = True
        db_table = "user_"


class Log(models.Model, model_sharding.ShardingMixin):
    level = models.PositiveSmallIntegerField(default=0)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(_('is_deleted'),
                                     default=False, help_text='是否删除')

    # Date-based sharding
    SHARDING_TYPE = 'date'
    SHARDING_DATE_START = '2020-03-01'
    SHARDING_DATE_FORMAT = '%Y'

    def __str__(self):
        return "%s %s %s" % (self.time, self.level, self.content)

    class Meta:
        abstract = True
        db_table = "log_"


class DeviceLog(models.Model, model_sharding.ShardingMixin):

    status = models.SmallIntegerField(
        _('status'), help_text='状态', default=0)
    is_deleted = models.BooleanField(_('is_deleted'),
                                     default=False, help_text='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, help_text='修改时间')

    # Date-based sharding
    SHARDING_TYPE = 'date'
    SHARDING_DATE_START = '2021-12-01'
    SHARDING_DATE_END = '2031-12-31'
    SHARDING_DATE_FORMAT = '%Y'

    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True
        db_table = "device_log_"


def init_models(admin_opts=None, abs_model=None):
    """

    :param admin_opts:
    :param abs_model:
    :return:
    """
    if not issubclass(abs_model, models.Model):
        raise TypeError(f"abs_model:{abs_model} not subclass of models.Model")
    if not issubclass(abs_model, model_sharding.ShardingMixin):
        raise TypeError(f"abs_model:{abs_model} not subclass of"
                        f" model_sharding.ShardingMixin")
    meta = getattr(abs_model, '_meta')
    model_sharding.register_admin_opts(meta.label_lower, admin_opts)
    for sharding in abs_model.get_sharding_list():
        model_sharding.create_model(abs_model, sharding,
                                    module_name="apps.demo.models")
    return


def init_user_models():
    admin_opts = {
        'list_display': ('id', 'user_name', 'name', 'age', 'active',
                         'created_at', 'updated_at')
    }
    return init_models(admin_opts=admin_opts, abs_model=User)


def init_log_models():
    admin_opts = {
        'list_display': ('id', 'time', 'level', 'content')
    }
    return init_models(admin_opts=admin_opts, abs_model=Log)


def init_device_log_models():
    admin_opts = {
        'list_display': ('id', 'status', 'create_time',
                         'update_time', 'is_deleted')
    }
    return init_models(admin_opts=admin_opts, abs_model=DeviceLog)


def auto_register():
    # 动态创建Model,同时注册到admin
    init_user_models()
    init_log_models()
    init_device_log_models()
    pprint.pprint(model_sharding.shard_tables)
    return


auto_register()
