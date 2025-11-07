#ifndef BREMSIM_STEPPING_ACTION_H
#define BREMSIM_STEPPING_ACTION_H 1

#include "G4UserSteppingAction.hh"
#include "G4LogicalVolume.hh"


namespace BremSim
{
    class SteppingAction : public G4UserSteppingAction
    {
        public: 
            SteppingAction();
            ~SteppingAction();

            void UserSteppingAction(const G4Step*) override;
        
        private:
            G4LogicalVolume* fBremsVolume = nullptr;
    };
}
#endif