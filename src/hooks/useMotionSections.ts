import { useEffect } from "react";

const MOTION_SELECTOR = "[data-motion-section]";

export function useMotionSections() {
  useEffect(function setupMotionSections() {
    const sections = Array.from(document.querySelectorAll<HTMLElement>(MOTION_SELECTOR));

    if (sections.length === 0) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      function handleIntersect(entries) {
        entries.forEach(function updateSection(entry) {
          entry.target.toggleAttribute("data-in-view", entry.isIntersecting);
        });
      },
      { rootMargin: "-10% 0px -10% 0px", threshold: 0.16 }
    );

    sections.forEach(function observeSection(section) {
      observer.observe(section);
    });

    let animationFrame = 0;

    function updateParallax() {
      animationFrame = 0;
      const viewportCenter = window.innerHeight / 2;

      sections.forEach(function setSectionParallax(section) {
        if (!section.hasAttribute("data-in-view")) {
          return;
        }

        const rect = section.getBoundingClientRect();
        const sectionCenter = rect.top + rect.height / 2;
        const distance = (viewportCenter - sectionCenter) / window.innerHeight;
        const clampedDistance = Math.max(-1, Math.min(1, distance));
        section.style.setProperty("--parallax-y", `${clampedDistance * 28}px`);
      });
    }

    function requestParallaxUpdate() {
      if (animationFrame !== 0) {
        return;
      }

      animationFrame = window.requestAnimationFrame(updateParallax);
    }

    requestParallaxUpdate();
    window.addEventListener("scroll", requestParallaxUpdate, { passive: true });
    window.addEventListener("resize", requestParallaxUpdate);

    return function cleanupMotionSections() {
      observer.disconnect();
      window.removeEventListener("scroll", requestParallaxUpdate);
      window.removeEventListener("resize", requestParallaxUpdate);

      if (animationFrame !== 0) {
        window.cancelAnimationFrame(animationFrame);
      }
    };
  }, []);
}
