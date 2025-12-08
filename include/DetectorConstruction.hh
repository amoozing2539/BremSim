#ifndef BREMSIM_DETECTORCONSTRUCTION_H
#define BREMSIM_DETECTORCONSTRUCTION_H 1


#include "G4VUserDetectorConstruction.hh"
#include "G4GenericMessenger.hh"


namespace BremSim
{
	class DetectorConstruction : public G4VUserDetectorConstruction
	{
	public:
		DetectorConstruction();
		~DetectorConstruction() override;

		G4VPhysicalVolume* Construct() override;

		G4LogicalVolume* GetBremsVolume() const { return fBremsVolume; };

	private:
		void DefineCommands();

		G4LogicalVolume* fBremsVolume = nullptr;
		class G4GenericMessenger* fMessenger = nullptr;
		G4double fFoilThickness = 0.05; // default value, unit will be handled by messenger or explicit multiplication
	};
}

#endif // BREMSIM_DETECTORCONSTRUCTION_H