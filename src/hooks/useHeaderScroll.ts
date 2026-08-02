import { useEffect, useState } from "react";

const SCROLLED_OFFSET = 12;

export function useHeaderScroll() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(function watchHeaderScroll() {
    function updateHeaderState() {
      const nextIsScrolled = window.scrollY > SCROLLED_OFFSET;

      setIsScrolled(function updateScrolledState(currentIsScrolled) {
        return currentIsScrolled === nextIsScrolled ? currentIsScrolled : nextIsScrolled;
      });
    }

    updateHeaderState();
    window.addEventListener("scroll", updateHeaderState, { passive: true });

    return function cleanupHeaderScroll() {
      window.removeEventListener("scroll", updateHeaderState);
    };
  }, []);

  return isScrolled;
}
