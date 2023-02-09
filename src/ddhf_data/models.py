# -*- coding: UTF-8 -*-
#
import PIL.Image as Image
import datetime
import ddhf
import logging
import os
from MySQLdb import Connect
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


def get_tinyname(self):
    """Expect a picture object as arg 1. """
    originalname = os.path.join(settings.MEDIA_ROOT, self.pictureoriginal.name)
    tinyname = originalname.replace("pictureoriginal","tiny")
    returnurl = self.pictureoriginal.url.replace("pictureoriginal", "tiny")
    if os.path.exists(tinyname) and os.path.getmtime(originalname) < os.path.getmtime(tinyname):
        return returnurl
    image = Image.open(originalname)
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")
    image.thumbnail((40, 40), Image.ANTIALIAS)
    image.save(tinyname, 'JPEG', quality=75)
    return format_html(returnurl)


def truncstrg(strg, size=40, more="..."):
        strg = strg.replace(", ,", "")
        if len(strg) > size:
            return strg[:size-len(more)] + more
        return strg[:size]


class Donators(models.Model):

    class Meta:
        db_table = 'donators'
        verbose_name = "donator"
        verbose_name_plural = "donatorer"
        ordering = ['donatorname',]


    donatorid           = models.AutoField("donator nr.", primary_key=True)
    creator             = models.CharField(max_length=12, null=False, verbose_name="oprettet af")
    created             = models.DateTimeField(verbose_name='oprettet', help_text="tidspunkt for registrering", auto_now_add=True)
    lastmodified        = models.DateTimeField(verbose_name='sidst rettet', auto_now=True)
    donatorinstitution  = models.CharField('firma/institution', help_text=u"hjalp", max_length=255, null=True, blank=True, db_index=True)
    donatorposition     = models.CharField('stilling', max_length=255, null=True, blank=True)
    donatorname         = models.CharField('navn', help_text="fornavn(e) efternavn(e)", max_length=255, null=False, db_index=True)
    donatoraddress      = models.CharField('adresse', help_text="adresse, postnummer og by", max_length=255, null=True, blank=True)
    donatorphone        = models.CharField('telefon', max_length=255, null=True, blank=True)
    donatoremail        = models.EmailField(verbose_name="email",max_length=255, null=True, blank=True)


    def __str__(self):
        return truncstrg(", ".join([
                            self.donatorinstitution or "institution missing",
                            self.donatorposition,
                            self.donatorname,
                            ])
                        )


class Files(models.Model):
    class Meta:
        db_table = 'files'
        verbose_name = "sag"
        verbose_name_plural = "sager"
        ordering = ['filetitle']

    fileid          = models.AutoField(verbose_name="sag nr.",primary_key=True)
    creator         = models.CharField(max_length=12, null=False, verbose_name="oprettet af")
    created         = models.DateTimeField(verbose_name='oprettet', help_text="tidspunkt for registrering", auto_now_add=True)
    lastmodified    = models.DateTimeField(verbose_name='sidst rettet', auto_now=True)
    filetitle       = models.CharField('Titel', max_length=255, null=True, blank=False)
    filedescription = models.TextField('beskrivelse', null=True, blank=True)
    datingfrom      = models.DateField(verbose_name="Datering fra", null=True, blank=False)
    datingto        = models.DateField(verbose_name="Datering til", null=True, blank=True)

    def was_created_today(self):
        return self.created.date() == datetime.date.today()

    def was_modified_today(self):
        return self.lastmodified.date() == datetime.date.today()

    def __str__(self):
        return truncstrg(", ".join((
                    self.filetitle or "title missing",
                    self.filedescription or "description missing",)
                    )
                )


class Pictures(models.Model):

    class Meta:
        db_table = 'pictures_dj'
        verbose_name = "billede"
        verbose_name_plural = "billeder"
        ordering = ['picturetext',]

    def picture_tag(self):
        return mark_safe(
            '<a href="%s"><img title="%s" src="%s"/></a>' % (
                os.path.join(settings.MEDIA_URL, self.pictureoriginal.name),
                self.picturetext,
                get_tinyname(self)
            )
        )

    picture_tag.short_description = "Billede"
    picture_tag.allow_tags = True

    pictureid           = models.AutoField(verbose_name="billede nr.", primary_key=True)
    picturetext         = models.TextField(verbose_name="beskrivelse", )
    pictureregisteredby = models.CharField(max_length=12, null=True, verbose_name="oprettet af")
    pictureregistered   = models.DateTimeField(verbose_name="registreret", auto_now_add=True) # date NOT NULL default '0000-00-00',
    lastmodified        = models.DateTimeField(verbose_name='rettet', auto_now=True)
    pictureoriginal     = models.ImageField(upload_to='pictureoriginal', verbose_name="billede", help_text="uploadet billede i oprindelig størrelse" ) # mediumblob
    picturemedium       = models.ImageField(upload_to='picturemedium', editable=False, ) # mediumblob
    picturelow          = models.ImageField(upload_to='picturelow', editable=False, ) # mediumblob

    def save(self, *args, **kwargs):
        super(Pictures, self).save(*args, **kwargs) # Call the "real" save() method.
        filename = os.path.join(settings.MEDIA_ROOT, self.pictureoriginal.name)
        ext = filename.rsplit('.', 1)[1]
        image = Image.open(filename)
        if image.mode not in ("L", "RGB"):
             image = image.convert("RGB")

        basename = os.path.basename(filename)
        self.picturemedium.name = u"picturemedium/" + basename
        filenamemedium = os.path.join(settings.MEDIA_ROOT, self.picturemedium.name)
        image.thumbnail((640, 640), Image.ANTIALIAS)
        image.save(filenamemedium, 'JPEG', quality=75)

        basename = os.path.basename(filename)
        self.picturelow.name = u"picturelow/" + basename
        filenamelow = os.path.join(settings.MEDIA_ROOT, self.picturelow.name)
        image.thumbnail((150, 150), Image.ANTIALIAS)
        image.save(filenamelow, 'JPEG', quality=75)
        super(Pictures, self).save(*args, **kwargs) # Call the "real" save() method.

        get_tinyname(self)
        # con = Connect(db=ddhf.settings.DATABASE_NAME,
        #             user=ddhf.settings.DATABASE_USER,
        #             passwd=ddhf.settings.DATABASE_PASSWORD,
        #             host=ddhf.settings.DATABASE_HOST, port=3306)
        # cursor = con.cursor()
        # sql = """delete from pictures where pictureid = %s"""
        # args = (self.pictureid,)
        # cursor.execute (sql, args)
        # sql = """INSERT INTO pictures (
        #              pictureid, picturetext, pictureregistered,
        #              pictureregisteredby, lastmodified
        #          )
        #          VALUES
        #          (%s,%s,%s,%s,%s)
        #       """
        #
        # args = (self.pictureid,
        #         self.picturetext,
        #         datetime.date(self.pictureregistered.year, self.pictureregistered.month, self.pictureregistered.day),
        #         self.pictureregisteredby,
        #         self.lastmodified,
        #        )
        # cursor.execute (sql, args)
        # con.commit()

    def __str__(self):
        return truncstrg(", ".join((
                            "%s" % (self.pictureid),
                            self.picturetext,
                            )),
                        )


class Subjects(models.Model):

    class Meta:
        db_table = 'subjects'
        verbose_name = "emnegruppe"
        verbose_name_plural = "emnegrupper"
        ordering = ['subjecttitle']

    subjectid           = models.AutoField(verbose_name="emnegruppe nr.", primary_key=True)
    creator             = models.CharField(max_length=12, null=False, verbose_name="oprettet af")
    # creator             = models.ForeignKey(User, db_column='creator', default="%s" % (User), null=False, verbose_name="oprettet af")
    created             = models.DateTimeField(verbose_name='oprettet', help_text="tidspunkt for registrering", auto_now_add=True)
    lastmodified        = models.DateTimeField(verbose_name='rettet', auto_now=True)
    subjecttitle        = models.CharField('navn', max_length=255, null=True, blank=False) # varchar(255) default NULL,
    subjectdescription  = models.TextField('beskrivelse', null=True, blank=True) # text,

    def __str__(self):
        return truncstrg( self.subjecttitle or "title string missing")


class Producers(models.Model):

    class Meta:
        db_table = 'producers'
        verbose_name = "producent"
        verbose_name_plural = "producenter"
        ordering = ["producertitle",]


    producerid          = models.AutoField(verbose_name="producent nr.", primary_key=True)
    creator             = models.CharField(max_length=12, null=False, verbose_name="oprettet af")
    # creator             = models.ForeignKey(User, db_column='creator', default="%s" % (User), null=False, verbose_name="oprettet af")
    created             = models.DateTimeField(verbose_name='oprettet', help_text="tidspunkt for registrering", auto_now_add=True)
    lastmodified        = models.DateTimeField(verbose_name='rettet', auto_now=True)
    producertitle       = models.CharField('navn', help_text="producent/fabrikant/forfatter", max_length=255, null=True, blank=False) # varchar(255) default NULL,
    producerdescription = models.TextField('beskrivelse', null=True, blank=True) # text,

    def __str__(self):
        return truncstrg( self.producertitle or "producer title missing")


class Sted(models.Model):
    class Meta:
        db_table = 'sted'
        verbose_name = "sted"
        verbose_name_plural = "steder"
    stednavn = models.CharField('stednavn', help_text="område/kommune/bynavn", max_length=60, null=True, blank=True)

    def __str__(self):
        return self.stednavn or "stednavn missing"



class Items(models.Model):
    status_as = (
      ("publiseret", (
          (0, 'godkendt'),
        ),
      ),
      ("redaktion", (
          (1, 'klar'),
          (2, 'kladde'),
        ),
      ),
      ("offline", (
          (3, u'udgået'),
          (4, 'intern'),
        ),
      ),
    )

    acquiretype_as = (
        (0, 'Ukendt'),
        (1, 'Gave'),
        (3, 'Køb'),
        (4, 'Deponering'),
    )

    class Meta:
        db_table = 'items'
        verbose_name = "genstand"
        verbose_name_plural = "genstande"
        ordering = ['itemheadline']

    def get_pictures(self):
        for p in self.itempicture.select_related():
            logger.debug(p.picturetext)
        # return mark_safe(
        #     "".join('<img class="tiny_img" title="%s" src="%s" />' % (p.picturetext, get_tinyname(p)) for p in self.itempicture.select_related())
        # )
        return mark_safe(
            "".join('<a href="%s"><img class="tiny_img" title="%s" src="%s" /></a>' % (p.pictureoriginal.url, p.picturetext, get_tinyname(p)) for p in self.itempicture.select_related())
        )

    get_pictures.short_description = "Billeder"
    get_pictures.allow_tags = True

    itemid              = models.AutoField(verbose_name="genstand nr.", primary_key=True, editable=False)
    itemtemporary       = models.IntegerField(blank=True, null=False, default=0)
    fileid              = models.ForeignKey(Files, db_column='fileid', null=False, verbose_name="sag nr.", on_delete=models.CASCADE)
    olditemid           = models.CharField(verbose_name="gammelt nr.", max_length=255, blank=True)
    itemdeleted         = models.IntegerField(verbose_name="status", choices=status_as, null=True, default=0)
    itemheadline        = models.CharField('betegnelse', max_length=255, blank=False, db_index=True)
    itemdescription     = models.TextField('beskrivelse', default='', blank=True)
    itemsize            = models.CharField('størrelse', max_length=255, blank=True)
    itemweight          = models.CharField('Vægt', max_length=255, blank=True)
    itemmodeltype       = models.CharField(verbose_name="model/type", max_length=255, blank=True)
    itemserialno        = models.CharField(verbose_name="serienummer", max_length=255, blank=True)
    itemdatingfrom      = models.DateField(verbose_name="Datering fra", null=True, blank=False)
    itemdatingto        = models.DateField(verbose_name="Datering til", null=True, blank=True)
    producerid          = models.ForeignKey(Producers, db_column="producerid", verbose_name='producent', help_text="producent/fabrikant/forfatter", null=True, blank=True, on_delete=models.CASCADE)
    itemacquiretype     = models.IntegerField(verbose_name="modtaget som", choices=acquiretype_as, null=True, blank=False, default=0)
    itemdepositeduntil  = models.DateField(verbose_name="deponeret/udlånt indtil", null=True, blank=True)
    donatorid           = models.ForeignKey(Donators, db_column="donatorid", verbose_name='donator', null=True, blank=True, on_delete=models.CASCADE)
    itemoutdated        = models.IntegerField("udgået",null=True, blank=True)
    itemborroweduntil   = models.DateField(verbose_name="udlånt indtil",null=True, blank=True)
    itemreceived        = models.DateField(verbose_name="modtagelsesdato", null=True, blank=True)
    itemreceivedby      = models.CharField("modtaget af", max_length=12, blank=True)
    itemregistered      = models.DateField(verbose_name="registreringsdato", null=True, blank=True)
    # itemregisteredby    = models.ForeignKey(User, db_column='itemregisteredby', default="%s" % (User), null=False, verbose_name="registreret af")
    itemregisteredby    = models.CharField(max_length=12, null=True, blank=True, verbose_name="oprettet af")
    lastmodified        = models.DateTimeField(verbose_name='rettet', null=True, auto_now=True)
    itemthanksletter    = models.DateField(verbose_name="takkebrev afsendt", null=True, blank=True)
    placementid         = models.IntegerField(verbose_name="placering", null=True, blank=True)
    # XXX Nyt felt
    itemlocation        = models.TextField("pladsering", db_column='itemlocation', blank=True, null=True)
    itemusedby          = models.TextField("brugt af", blank=True)
    itemusedfor         = models.TextField("til hvad", blank=True)
    itemusedwhere       = models.TextField("hvor", blank=True)
    itemusedwhereid     = models.ForeignKey(Sted, null=True, blank=True, db_column='itemusedwhereid', verbose_name="brugt i geografisk område", on_delete=models.CASCADE)
    itemusedfrom        = models.DateField(verbose_name="brugt fra", null=True, blank=True)
    itemusedto          = models.DateField(verbose_name="brugt indtil", null=True, blank=True)
    itemusedendfrom     = models.DateField(verbose_name="udgået af brug/nedtaget", null=True, blank=True)
    itemusedendto       = models.DateField(verbose_name="udgået af brug/nedtaget", null=True, blank=True)
    itemextrainfo       = models.TextField("særlige oplysninger", blank=True)
    itemrestoration     = models.TextField("restaurering", blank=True)
    itemreferences      = models.TextField("litteraturhenvisninger", blank=True)
    itemremarks         = models.TextField("bemærkninger", help_text="internt brug", blank=True)
    iteminternal        = models.IntegerField("intern", help_text="forenigens aktiv", default=0, null=False, blank=True)
    itemsubject         = models.ManyToManyField(Subjects, related_name="itemlist", verbose_name="emnegrupper" ,null=True, blank=True)
    itempicture         = models.ManyToManyField(Pictures, verbose_name="billeder" , null=True, blank=True)

    def __str__(self):
        return truncstrg( self.itemheadline)


