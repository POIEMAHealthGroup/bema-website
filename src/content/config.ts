import { defineCollection, z } from 'astro:content';

const teamCollection = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    title: z.string(),
    imageLabel: z.string(),
    bio: z.string(),
    order: z.number().default(0),
    draft: z.boolean().default(false),
  }),
});

// RESERVED: Not active at Phase 1.1
const eventsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.date(),
    endDate: z.date().optional(),
    time: z.string().optional(),
    location: z.string(),
    image: z.string().startsWith('/uploads/events/'),
    summary: z.string(),
    tags: z.array(z.string()).optional(),
    registrationLink: z.string().url().optional(),
    registrationRequired: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

// RESERVED: Not active at Phase 1.1
const sermonsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    slug: z.string().optional(),
    date: z.date(),
    speaker: z.string(),
    series: z.string().optional(),
    scripture: z.string().optional(),
    audioUrl: z.string().url().optional(),
    videoUrl: z.string().url().optional(),
    image: z.string().startsWith('/uploads/sermons/').optional(),
    summary: z.string().optional(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().default(false),
  }),
});

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    slug: z.string().optional(),
    pubDate: z.date(),
    description: z.string(),
    author: z.string().default("David Knight"),
    image: z.object({
      url: z.union([
        z.string().startsWith('/images/'),
        z.string().startsWith('/uploads/blog/'),
      ]),
      alt: z.string(),
    }).optional(),
    tags: z.array(z.string()).default(["healthcare-access"]),
    draft: z.boolean().default(false),
  }),
});

const siteInfoCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    siteName: z.string().optional(),
    siteDescription: z.string().optional(),
    organizationName: z.string().optional(),
    contactEmail: z.string().optional(),
    contactPhone: z.string().optional(),
    address: z.string().optional(),
  }),
});

export const collections = {
  team: teamCollection,
  events: eventsCollection,
  sermons: sermonsCollection,
  blog: blogCollection,
  siteInfo: siteInfoCollection,
};
