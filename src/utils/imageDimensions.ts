// Intrinsic pixel dimensions measured from the corresponding files in public.
const dimensions: Record<string, { width: number; height: number }> = {
  "/images/BEMA-Misc.jpg": { width: 1200, height: 800 },
  "/images/BEMA-Misc4.jpg": { width: 1200, height: 800 },
  "/images/BEMA-misc3.jpg": { width: 1200, height: 800 },
  "/images/about-story.jpg": { width: 1200, height: 800 },
  "/images/blog-direct-primary-care.jpg": { width: 1200, height: 800 },
  "/images/blog-healthcare-access.jpg": { width: 1200, height: 800 },
  "/images/blog-mental-health.jpg": { width: 1200, height: 800 },
  "/images/clinics/eagle-vision-eye-care.webp": { width: 1200, height: 761 },
  "/images/clinics/newgen-primary-care.webp": { width: 1200, height: 761 },
  "/images/clinics/uplift-psychotherapy-center.webp": { width: 1200, height: 761 },
  "/images/employers-program.jpg": { width: 1200, height: 800 },
  "/images/home-hero.jpeg": { width: 1600, height: 1200 },
  "/images/home-who-we-serve.jpg": { width: 1200, height: 800 },
  "/images/providers-clinic-network.jpg": { width: 1200, height: 800 },
  "/images/services-eye-care.jpg": { width: 1200, height: 800 },
  "/images/services-primary-care.jpg": { width: 1200, height: 800 },
  "/images/team/founders-team-portrait.webp": { width: 880, height: 1199 },
};

export function imageDimensions(src: string) {
  return dimensions[src];
}
