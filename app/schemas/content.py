from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

NonEmptyText = Annotated[str, Field(min_length=1)]


class ContentModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Brand(ContentModel):
    name: NonEmptyText


class NavigationLink(ContentModel):
    label: NonEmptyText
    href: NonEmptyText


class Navigation(ContentModel):
    links: list[NavigationLink] = Field(min_length=1)
    cta: NonEmptyText


class Hero(ContentModel):
    badge: NonEmptyText
    titleLines: list[NonEmptyText] = Field(min_length=1)
    subtitle: NonEmptyText
    primaryCta: NonEmptyText
    secondaryCta: NonEmptyText
    trustNote: NonEmptyText
    imageUrl: NonEmptyText
    imageAlt: NonEmptyText
    experience: NonEmptyText
    experienceLabel: NonEmptyText


class Statistic(ContentModel):
    value: NonEmptyText
    label: NonEmptyText


class About(ContentModel):
    eyebrow: NonEmptyText
    titleBefore: NonEmptyText
    titleAccent: NonEmptyText
    bioFirst: NonEmptyText
    bioSecond: NonEmptyText
    imageUrl: NonEmptyText
    imageAlt: NonEmptyText
    keywords: list[NonEmptyText] = Field(min_length=1)
    stats: list[Statistic] = Field(min_length=1)


class Service(ContentModel):
    title: NonEmptyText
    description: NonEmptyText


class Services(ContentModel):
    eyebrow: NonEmptyText
    titleBefore: NonEmptyText
    titleAccent: NonEmptyText
    titleAfter: NonEmptyText
    intro: NonEmptyText
    cta: NonEmptyText
    items: list[Service] = Field(min_length=1)


class Testimonial(ContentModel):
    initials: NonEmptyText
    tag: NonEmptyText
    quote: NonEmptyText


class Testimonials(ContentModel):
    eyebrow: NonEmptyText
    titleBefore: NonEmptyText
    titleAccent: NonEmptyText
    intro: NonEmptyText
    items: list[Testimonial] = Field(min_length=1)


class Contact(ContentModel):
    eyebrow: NonEmptyText
    titleBefore: NonEmptyText
    titleAccent: NonEmptyText
    titleAfter: NonEmptyText
    intro: NonEmptyText
    email: NonEmptyText
    phone: NonEmptyText
    location: NonEmptyText


class Footer(ContentModel):
    description: NonEmptyText
    contactHeading: NonEmptyText
    followHeading: NonEmptyText
    privacyTitle: NonEmptyText
    copyright: NonEmptyText


class HomepageContent(ContentModel):
    brand: Brand
    navigation: Navigation
    hero: Hero
    marquee: list[NonEmptyText] = Field(min_length=1)
    about: About
    services: Services
    testimonials: Testimonials
    contact: Contact
    footer: Footer
