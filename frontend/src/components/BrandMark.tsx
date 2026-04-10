type BrandMarkProps = {
  className?: string;
  labelClassName?: string;
  title?: string;
};

export function BrandMark({
  className = "",
  labelClassName = "",
  title = "metroGen",
}: BrandMarkProps) {
  return (
    <div
      aria-hidden="true"
      className={[
        "brand-mark inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-line bg-white text-[1.8rem] font-bold text-[#2563eb] shadow-panel",
        className,
      ].join(" ")}
      title={title}
    >
      <span className={["brand-mark__letter leading-none", labelClassName].join(" ")}>g</span>
    </div>
  );
}
