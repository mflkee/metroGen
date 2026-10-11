import { type ReactNode } from "react";

import { AppDialog } from "@/components/ui/app-dialog";

type ModalProps = {
  title: string;
  description?: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  size?: "default" | "sm" | "xl";
};

/**
 * The app's modal — now the fleet dialog (`@metro/app-dialog`) behind the name the screens use.
 *
 * The contract comes from the fleet: the backdrop does **not** close the dialog, only an explicit
 * close control or the Escape key does (the hand-rolled modal used to close on a backdrop click),
 * and Radix supplies the focus trap, the aria wiring and the scroll lock.
 */
export function Modal({ title, description, open, onClose, children, footer, size }: ModalProps) {
  return (
    <AppDialog
      description={description}
      footer={footer}
      open={open}
      size={size}
      title={title}
      onClose={onClose}
    >
      {children}
    </AppDialog>
  );
}
