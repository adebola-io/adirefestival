import type { MouseEvent, RefObject, SyntheticEvent } from "react";
import type { LookbookItem } from "../types";

interface PreviewDialogProps {
  dialogRef: RefObject<HTMLDialogElement | null>;
  item: LookbookItem | null;
  onBackdropClick: (event: MouseEvent<HTMLDialogElement>) => void;
  onCancel: (event: SyntheticEvent<HTMLDialogElement, Event>) => void;
  onClose: () => void;
}

export function PreviewDialog({ dialogRef, item, onBackdropClick, onCancel, onClose }: PreviewDialogProps) {
  return (
    <dialog className="preview-dialog" aria-label="Lookbook image preview" ref={dialogRef} onCancel={onCancel} onClick={onBackdropClick} aria-modal="true">
      <button className="preview-close" type="button" aria-label="Close image preview" onClick={onClose}>
        Close
      </button>
      {item ? <img src={item.src} alt={item.alt} /> : null}
    </dialog>
  );
}
