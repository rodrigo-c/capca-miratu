export default function Header() {
  return (
    <div className="navbar-dark">
      <img src={`${import.meta.env.BASE_URL}capca-white.svg`} alt="CAPCA" className="navbar-logo" />
      <span className="navbar-title">DimeTú</span>
    </div>
  );
}
