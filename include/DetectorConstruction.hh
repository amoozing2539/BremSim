#ifndef BREMSIM_DETECTORCONSTRUCTION_H
#define BREMSIM_DETECTORCONSTRUCTION_H 1


#include "G4VUserDetectorConstruction.hh"


namespace BremSim
{
	class DetectorConstruction : public G4VUserDetectorConstruction
	{
	public:
		DetectorConstruction() = default;
		~DetectorConstruction() override = default;

		G4VPhysicalVolume* Construct() override;

		G4LogicalVolume* GetBremsVolume() const { return fBremsVolume; };

	private:
		G4LogicalVolume* fBremsVolume = nullptr;
	};
}

#endif // BREMSIM_DETECTORCONSTRUCTION_H