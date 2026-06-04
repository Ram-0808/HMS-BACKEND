from django.db import models


class SiteSetting(models.Model):
    """
    Singleton model — only one row exists.
    Stores all configurable content for the public website.
    """

    # Images
    hospital_image = models.ImageField(
        upload_to='site/', blank=True, null=True,
        help_text="Hospital building photo for the About Us page"
    )

    # About Us
    hero_tagline = models.CharField(
        max_length=300, default='Where Care Meets Compassion',
        help_text="Main tagline shown on the About Us hero section"
    )
    about_story = models.TextField(
        blank=True, default='',
        help_text="The 'Our Story' paragraph text"
    )

    # Vision
    vision_statement = models.TextField(
        blank=True, default='',
        help_text="The vision quote displayed on Vision & Mission page"
    )

    # Contact
    phone = models.CharField(max_length=20, blank=True, default='')
    emergency_phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    address = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=200, blank=True, default='')

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site_settings'
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton — only one row ever exists
        if not self.pk and SiteSetting.objects.exists():
            self.pk = SiteSetting.objects.first().pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the singleton instance, create if it doesn't exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryImage(models.Model):
    """Gallery images for the Services page carousel."""

    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True, default='')
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        db_table = 'gallery_images'

    def __str__(self):
        return self.caption or f"Gallery image {self.id}"
