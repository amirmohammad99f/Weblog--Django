from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django_jalali.db import models as jmodels
from django.urls import reverse
from django_resized import ResizedImageField
from django.template.defaultfilters import slugify


# Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
        REJECTED = "RJ", "Rejected"

    CategoryChoices = (
        ('تکنولوژی', 'تکنولوژی'),
        ('زبان برنامه نویسی', 'زبان برنامه نویسی'),
        ('هوش مصنوعی', 'هوش مصنوعی'),
        ('بلاکچین', 'بلاکچین'),
        ('سایر', 'سایر'),
    )

    # relations
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='نویسنده')
    # data fields
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField()
    slug = models.SlugField(max_length=200, verbose_name='اسلاگ')
    # date
    publish = jmodels.jDateTimeField(default=timezone.now,
                                     verbose_name='تاریخ انتشار')
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    # choice fields
    status = models.CharField(max_length=2, choices=Status.choices,
                              default=Status.DRAFT, verbose_name='وضعیت')
    reading_time = models.PositiveIntegerField(verbose_name="زمان مطالعه")
    category = models.CharField(choices=CategoryChoices, max_length=20,
                                default='سایر')
    # manager
    # objects = models.Manager()
    objects = jmodels.jManager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:posts_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for img in self.images.all():
            storege, path = img.image_file.storage, img.image_file.path
            storege.delete(path)
        super().delete(*args, **kwargs)


class Ticket(models.Model):
    message = models.TextField(verbose_name='پیام')
    name = models.CharField(max_length=150, verbose_name='نام')
    phone = models.CharField(max_length=11, verbose_name='شماره تلفن')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=250, verbose_name='موضوع')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'

    def __str__(self):
        return self.subject


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='پست')
    body = models.TextField(verbose_name='متن کامنت')
    name = models.CharField(max_length=150, verbose_name='نام')
    created = jmodels.jDateTimeField(auto_now_add=True,
                                     verbose_name='تاریخ ایجاد')
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')
    active = models.BooleanField(default=False, verbose_name='وضعیت')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'

    def __str__(self):
        return f"{self.name}:{self.post}"


def year_directory_path(image, filename):
    return f'{image.post.created.year}/{filename}'


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='images', verbose_name='تصویر')
    image_file = ResizedImageField(upload_to='post_images/',
                                   size=[600, 400],
                                   quality=75, crop=['middle', 'center'])
    title = models.CharField(max_length=200, verbose_name='عنوان', null=True,
                             blank=True)
    description = models.TextField(verbose_name='توضیحات', null=True,
                                   blank=True)
    created = jmodels.jDateTimeField(auto_now_add=True,
                                     verbose_name='تاریخ ایجاد')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = 'تصویر'
        verbose_name_plural = 'تصاویر'

    def delete(self, *args, **kwargs):
        storage, path = self.image_file.storage, self.image_file.path
        storage.delete(path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title if self.title else self.image_file.name


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True,
                                null=True)
    birth_of_date = jmodels.jDateField(auto_now_add=True,
                                       verbose_name='تاریخ تولد', blank=True,
                                       null=True)
    bio = models.TextField(verbose_name='بایو', blank=True, null=True)
    photo = ResizedImageField(verbose_name='تصویر', upload_to='account_images/',
                              size=[600, 400],
                              quality=75, crop=['middle', 'center'], blank=True,
                              null=True)
    job = models.CharField(max_length=50, verbose_name='شغل', blank=True,
                           null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'اکانت'
        verbose_name_plural = 'اکانت ها'
