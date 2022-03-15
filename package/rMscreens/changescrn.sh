
#! /bin/bash

#Backup existing screens: changescr -b
#Change Screen: changescrn -c [SCREEN] -n [PATH TO NEW SCREEN]
#Restore original screens: changescrn -r [SCREEN] (use option 'all' to restore all screens at once)
#[SCREEN] options: batteryempty | lowbattery | overheating | poweroff | rebooting | recovery | splash | starting | suspended 

while getopts "r: c: n: :b" opt; do
	case $opt in
		r) #Restores original screen
			case $OPTARG in 
				batteryempty | lowbattery | overheating | poweroff | rebooting | recovery | splash | starting | suspended)
					echo "restoring $OPTARG.png..."
					cp /usr/share/remarkable/backupscrns/$OPTARG.png /usr/share/remarkable >&2
					echo "Done!"
					;;
				all)
					echo "Restoring all screens..."
					cp /usr/share/remarkable/backupscrns/*.png /usr/share/remarkable
					echo "Done!"
					;;
				*)
					echo "Screen Options: batteryempty lowbattery overheating poweroff rebooting recovery splash starting suspended"
					exit 1
					;;
			esac	
			;;

		c) #Specifies which screen to change. Must be used in combination with -n
			SCREEN=$OPTARG
		   case $NEWSCRN in 
		   		"") echo "Please specify location of new screen" 
					echo "Usage: changescrn -c [SCREEN] -n [PATH TO NEW SCREEN]"
					;;
			esac
		   ;;

		n) #Specifies location of new screen.  Must be used in combination with -c
			NEWSCRN=$OPTARG
		   case $SCREEN in 
		   		batteryempty | lowbattery | overheating | poweroff | rebooting | recovery | splash | starting | suspended)
				cp $NEWSCRN /usr/share/remarkable/$SCREEN.png
				;;
    	     	*)
    	     	echo "You either didn't specify a screen option first or didn't specify a correct screen option"
    	     	echo "Usage: changescrn -c [SCREEN] -n [PATH TO NEW SCREEN]"
    	     	echo "[SCREEN] options: batteryempty | lowbattery | overheating | poweroff | rebooting | recovery | splash | starting | suspended"
    	     	;;
    	     esac
    	   
		   ;;	
		b) #Creates a backup of original screens
			mkdir /usr/share/remarkable/backupscrns
			cp /usr/share/remarkable/*.png /usr/share/remarkable/backupscrns
		   ;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			exit 1
			;;
		:)
			echo "Option -$OPTARG requires and argument." >&2
			echo "Usage: changescrn -c [SCREEN] -n [PATH TO NEW SCREEN]"
			exit 1
			;;
	esac

	
done
