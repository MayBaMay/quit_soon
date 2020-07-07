GENERAL

note: modifiable variables found in (abstracts/variables)

LAYOUT
----------------------
----------------------

----------------------panels

1) add panelsto main content

<main>
    <section class="panel p4 pc-3">
    </section>
 </main>

class guide:
panel : general panel styling
p4: panel identifier for grid layout
pc-3: panel colour 3 (see variables in abstracts/variables)

2) create layout in page (e.g. pages/home.scss)
e.g. 

 grid-template-areas:
      "p1 p1 p1 p1 p1 p1 p1 p1 p1 p1 p1 p1"
      "p2 p2 p2 p2 p2 p2 p2 p2 p2 p2 p2 p2"

      "p5 p5 p5 p5 p5 p5 p6 p6 p6 p6 p6 p6"
      ". . . . . . . . . . . . "
      ". p3 p3 p3 p3 p4 p4 . . . . . ";

    .p1 {
      grid-area: p1;
    }

    explanation: 
    grid-template-areas creates the grid structure
    grid-area sets the position of grid-item

    NOTE: create different grid structures at different breakpoints for responsive design

----------------------modals
add new modal 
add to <div class="modal"> at bottom of page

e.g.

<div id="modal-2" class="modal-content">
    <section>
        <h4>Modal 2</h4>
        <p>
        Lorem ipsum dolor sit
        </p>
    </section>
</div>

guide:
use unique id
use class modal-content

toggle (to open modal)
e.g.
<button class="btn toggle-modal" data-modal="modal-2">
    modal
 </button>
guide: 
use class toggle-modal
use data-modal attribute to target modal id (in this example id="modal-2")

 





UTILITY CLASSES
----------------------
----------------------

------------------buttons

utility classes:
prefix: btn

suffices:
//colour

-primary
-secondary
-error
-success

//type
(default)
-cta [call to action]
-fab [floating action btn]
-text
-outline


e.g. <button class="btn-success-cta">VERIFY</button>

