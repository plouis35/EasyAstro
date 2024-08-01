import matplotlib.pyplot as plt

def show_lines(ax = None, show_line = True):
    """
    Show lines onto a plot. 
        
    Parameters
    ----------    
    ax : AxesSubplot
        The axis onto which the emission/absoption lines needs to be plotted.
        If ax = None, then the plotting function uses plt, rather than axis.
        
    show_line : bool
        Whether or not to draw vertical dashed lines. Default is True.
    
    Returns
    -------
    None
    
    """
    
    lines_to_display = [
        {"name" : 'Zero Order',"label" :'Zero', "lambda" :0.00}, 
        {"name" : 'Hydrogen', "label" : 'Hα',  "lambda" :656.2852}, 
        {"name" : 'Hydrogen', "label" : 'Hβ',  "lambda" :486.133 },
        {"name" : 'Hydrogen', "label" : 'Hγ',  "lambda" :434.047}, 
        {"name" : 'Hydrogen', "label" : 'Hδ',  "lambda" :410.174}, 
        {"name" : 'Hydrogen', "label" : 'Hε',  "lambda" :397.007}, 
        {"name" : 'Hydrogen', "label" : 'Hζ',  "lambda" :388.9049}, 
        {"name" : 'Hydrogen', "label" : 'Hη',  "lambda" :383.5384}, 
        {"name" : 'Hydrogen', "label" : 'Hθ',  "lambda" :379.75} , 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :527.04}, 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :516.89}, 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :495.76}, 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :466.81}, 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :438.36}, 
        {"name" : 'Iron', "label" : 'Fe',  "lambda" :430.79}, 
        {"name" : 'Magnesium', "label" : 'MgII',  "lambda" :448.11}, 
        {"name" : 'Magnesium', "label" : 'Mg',  "lambda" :518.36}, 
        {"name" : 'Magnesium', "label" : 'Mg',  "lambda" :517.27}, 
        {"name" : 'Magnesium', "label" : 'Mg',  "lambda" :516.73}, 
        {"name" : 'Neon', "label" : 'NeI',  "lambda" :585.249}, 
        {"name" : 'Neon', "label" : 'NeI',  "lambda" :588.189}, 
        #{"name" : 'Mercury', "label" : 'Hg',  "lambda" :404.656}, 
        #{"name" : 'Mercury', "label" : 'Hg',  "lambda" :435.833}, 
        #{"name" : 'Mercury', "label" : 'Hg',  "lambda" :546.074}, 
        #{"name" : 'Mercury', "label" : 'Hg',  "lambda" :576.960}, 
        #{"name" : 'Mercury', "label" : 'Hg',  "lambda" :578.966}, 
        {"name" : 'Sodium', "label" : 'NaI',  "lambda" :589.00}, 
        {"name" : 'Sodium', "label" : 'NaI',  "lambda" :589.59}, 
        {"name" : 'Oxygen', "label" : 'O1',  "lambda" :615.82}, 
        {"name" : 'Oxygen', "label" : 'O2',  "lambda" :627.77}, 
        {"name" : 'Oxygen', "label" : 'O2',  "lambda" :686.9}, 
        {"name" : 'Oxygen', "label" : 'O2',  "lambda" :718.6}, 
        {"name" : 'Oxygen', "label" : 'O2',  "lambda" :760.5}, 
        {"name" : 'Oxygen', "label" : 'O2',  "lambda" :898.77}, 
        {"name" : 'Oxygen', "label" : 'OIII',  "lambda" :495.9}, 
        {"name" : 'Oxygen', "label" : 'OIII',  "lambda" :500.69}, 
        {"name" : 'Water', "label" : 'H2O',  "lambda" :651.65}, 
        {"name" : 'Water', "label" : 'H2O',  "lambda" :694.07}, 
        {"name" : 'Water', "label" : 'H2O',  "lambda" :695.64}, 
        {"name" : 'Water', "label" : 'H2O',  "lambda" :698.90}, 
        {"name" : 'Calcium', "label" : 'Ca+ H',  "lambda" :396.85}, 
        {"name" : 'Calcium', "label" : 'Ca+ K',  "lambda" :393.37}, 
        {"name" : 'Helium', "label" : 'He I',  "lambda" :706.52}, 
        {"name" : 'Helium', "label" : 'He I',  "lambda" :667.82}, 
        {"name" : 'Helium', "label" : 'He I',  "lambda" :587.56}, 
        {"name" : 'Helium', "label" : 'He I',  "lambda" :501.57}, 
        {"name" : 'Helium', "label" : 'He I',  "lambda" :447.148}, 
        {"name" : 'Silicon', "label" : 'Si II',  "lambda" :634.71}, 
        {"name" : 'Silicon', "label" : 'Si II',  "lambda" :637.14}, 
        {"name" : 'Terbium', "label" : 'Tb',  "lambda" :487.7}, 
        {"name" : 'Terbium', "label" : 'Tb',  "lambda" :542.4}, 
        {"name" : 'Europium', "label" : 'Eu',  "lambda" :611.6}, 
        {"name" : 'Titanium', "label" : 'Ti+',  "lambda" :336.11}
    ]

    if (ax == None):
        ax = plt.gca()
        
    xbounds = ax.get_xbound()   # Getting the x-range of the plot     
    for ii in range(len(lines_to_display)):
        lam = lines_to_display[ii]['lambda'] * 10    # nm to AA
        if (lam > xbounds[0]) & (lam < xbounds[1]):
            ax.axvline(lam, 0.95, 1.0, color = 'red', lw = 1.0)
            ax.axvline(lam, color = 'red', lw = 0.3, linestyle = ':')
            trans = ax.get_xaxis_transform()
            ax.annotate(lines_to_display[ii]['label'], xy = (lam, 1.05), xycoords = trans, \
                     fontsize = 8, rotation = 90, color = 'red')

