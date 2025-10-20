//Define the world, foil, and sensitive detector. Geometries

#include "DetectorConstruction.hh"
#include "G4Box.hh"
#include "G4NistManager.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SDManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4VPhysicalVolume.hh"

#include "SensitiveDetector.hh" 

DetectorConstruction::DetectorConstruction() {}
DetectorConstruction::~DetectorConstruction() {}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
	G4NistManager* nist = G4NistManager::Instance();
	G4Material* world_mat = nist->FindOrBuildMaterial("G4_AIR");
	G4Material* foil_mat = nist->FindOrBuildMaterial("G4_W"); //Tungsten target material
	G4Material* detector_mat = nist->FindOrBuildMaterial("G4_Galactic");

	// World
	G4Box* solidWorld = new G4Box("World", 1.0 * m, 1.0 * m, 1.0 * m); 
	G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, world_mat, "logicWorld");
	G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "physWorld", 0, false, 0, true); //place world centered at (0,0,0)

	// Foil
	G4double foil_thickness = .01 * mm;
	G4double foil_xy = 10.0 * cm;
	G4Box* solidFoil = new G4Box("Foil", 0.5 * foil_xy, .5 * foil_xy, .5 * foil_thickness); //foil that is ~2mm thick 
	G4LogicalVolume* logicFoil = new G4LogicalVolume(solidFoil, foil_mat, "logicFoil");
	new G4PVPlacement(0, G4ThreeVector(0, 0, 0), logicFoil, "physFoil", logicWorld, false, 0, true);

	// Sensitive Detector
	G4double detector_thickness = .05 * mm;
	G4double detector_xy = 30.0 * cm;
	G4ThreeVector detector_pos = G4ThreeVector(0, 0, (0.5 * foil_thickness) + (0.5 * detector_thickness) + (1.0 * mm)); //as close to the foil as possible (1mm).
	G4Box* solidDetector = new G4Box("Detector", 0.5 * detector_xy, 0.5 * detector_xy, 0.5 * detector_thickness);
	G4LogicalVolume* logicDetector = new G4LogicalVolume(solidDetector, detector_mat, "logicalDetector");
	new G4PVPlacement(0, detector_pos, logicDetector, "physDetector", logicWorld, false, 0, true);

	// make detector volume a sensitive detector
	auto aSensitiveDetector = new SensitiveDetector("SensitiveDetector");
	logicDetector->SetSensitiveDetector(aSensitiveDetector);

	return physWorld;
}