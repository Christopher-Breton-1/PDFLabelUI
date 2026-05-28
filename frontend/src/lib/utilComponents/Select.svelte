<script>
    import {onDestroy, onMount,} from "svelte";
    import {setStore} from "../../stores/customStores.js";


    let mousePosX = 0;
    let mousePosY = 0;
    let mouseInContainer = false;
    let mouseDown = false;
    let mouseMove = false;
    let containerDims = {};
    let selStartX = null;
    let selStartY = null;
    let selectDiv = null;
    let isSelecting = false;
    let selDirection = null;
    let ctrlKeyPressed = false;
    let shiftKeyPressed = false;
    let allSelected = false;
    let scrollContainerDims;

    $:{
        scrollContainer?scrollContainerDims = scrollContainer.getBoundingClientRect():null;
    }

    // export let currentClickedElm = null;
    export let bgCol = "rgba(0,125,255,0.3)";
    export let borderStyle = "1px dashed blue";
    export let containerDiv = null;
    export let selectableElements = null;
    export let selectMode = "intersect"; //TODO: need to refine the logic for engulf.
    export let clearOnMouseDown = true;
    export let enableSelectAll = true;
    export let throttle = 0;
    export let dragSelect = true;
    export let clickSelect = true;
    export let ctrlSel = true;
    export let shiftSel = true;
    export let onSelect = () => {}; // TODO could be used to confer the selecting state or smth
    export let selectedElms = setStore({});
    export let scrollOnSelect = true;
    export let scrollContainer = null;
    export let checkTransform = false; // for accurate selection of transformed elements. TODO
    export let syncDepth = 1; // How deep do you sync?  TODO: Use this instead of the syncChildren flag. Depth = 0 is no sync. -1 = all sync

    $: if (shiftSel || ctrlSel) {
        window.addEventListener("keydown", handleKeyDown);
        window.addEventListener("keyup", handleKeyUp);
    }


    $: isSelecting = mouseInContainer && mouseDown && mouseMove && dragSelect;

    $: {
        if (isSelecting) {
            if (containerDiv !== null && selStartY !== null && selStartX !== null) {
                const selDivExists = !!selectDiv;
                if (!selDivExists) {

                    const newElement = document.createElement("div");
                    newElement.classList.add("select-box");
                    newElement.id = "select-div";

                    newElement.style.position = "absolute";
                    newElement.style.backgroundColor = bgCol;
                    newElement.style.border = borderStyle;
                    newElement.style.padding = "0"
                    newElement.style.margin = "0"
                    newElement.style.zIndex = "1000";
                    newElement.style.top = "0";
                    newElement.style.left = "0";

                    containerDiv.appendChild(newElement);
                    selectDiv = newElement;
                }

                // clamp mouse positions to container bounds
                const clampedMouseX = Math.max(
                    containerDims.left,
                    Math.min(mousePosX, containerDims.right)
                );

                const clampedMouseY = Math.max(
                    containerDims.top,
                    Math.min(mousePosY, containerDims.bottom)
                );

                const adjustedMouseX = (clampedMouseX - containerDims.left);
                const adjustedMouseY = (clampedMouseY - containerDims.top);

                if (selectMode==="dual"){
                    const NS = adjustedMouseY < selStartY ? 'N' : 'S'
                    const EW = adjustedMouseX < selStartX ? 'W' : 'E'
                    selDirection = NS + EW;
                }
                if (selectMode==="dual-reversed"){
                    const NS = adjustedMouseY < selStartY ? 'S' : 'N'
                    const EW = adjustedMouseX < selStartX ? 'E' : 'W'
                    selDirection = NS + EW;
                }

                const startX = Math.min(selStartX, adjustedMouseX);
                const startY = Math.min(selStartY, adjustedMouseY);
                const width = Math.abs(adjustedMouseX - selStartX);
                const height = Math.abs(adjustedMouseY - selStartY);

                // update styles
                selectDiv.style.top = `${startY}px`;
                selectDiv.style.left = `${startX}px`;
                selectDiv.style.width = `${width}px`;
                selectDiv.style.height = `${height}px`;

            }
        }
    }

    $:{
        if (containerDiv) {
            updateContainerDims();
        }
    }


    // throttle function to limit event handling frequency
    let lastCall = 0;

    function _throttle(callback, limit) {
        return function (...args) {
            const now = Date.now();
            if (now - lastCall >= limit) {
                lastCall = now;
                callback(...args);
            }
        };
    }

    function mouseMoveImpl(e) {
        if (mouseDown) {
            mouseMove = true;
        }
        mousePosY = e.clientY;
        mousePosX = e.clientX;
    }

    const throttledMouseMove = _throttle(mouseMoveImpl, throttle);

    function handleMouseMove(e) {
        e.preventDefault();
        throttledMouseMove(e);
        if (isSelecting) {
            handleDragSelect();
            scrollContainerOnEdge(e);
        }

    }
    function handleKeyDown(e) {
        if (e.key === "Control") {
            ctrlKeyPressed = true;
        } else if (e.key === "Shift") {
            shiftKeyPressed = true;
        } else if (enableSelectAll && e.ctrlKey && e.key === "a") {
            e.preventDefault();
            selectAllHandler();

        }
    }
    function handleKeyUp(e) {
        if (e.key === "Control") {
            ctrlKeyPressed = false;
        } else if (e.key === "Shift") {
            shiftKeyPressed = false;
        }

    }

    function checkMouseInContainer(e){
        const insideX = e.clientX >= containerDims.left && mousePosX <= containerDims.right;
        const insideY = e.clientY >= containerDims.top && mousePosY <= containerDims.bottom;
        mouseInContainer = insideX && insideY;
    }

    function disablePointerEvents(){
        const styleTag = document.createElement("style");
        styleTag.id = "disable-pointer-events";
        styleTag.textContent = `
            * {
                pointer-events: none !important;
                cursor: default !important;
            }
        `;
        document.head.appendChild(styleTag);
    }

    function enablePointerEvents(){
        const styleTag = document.getElementById("disable-pointer-events");
        if (styleTag) {
            document.head.removeChild(styleTag);
        }
    }

    function handleMouseDown(e){
        updateContainerDims(); // This must be first.

        checkMouseInContainer(e)
        e.preventDefault()
        mouseDown = true;

        if (dragSelect && mouseInContainer){
            selStartY = e.clientY - containerDims.top;
            selStartX = e.clientX - containerDims.left;
        }

        if (mouseInContainer && containerDiv) {
            if (scrollOnSelect) {
                scroll(e);
                if (!scrollContainer) {
                    scrollContainer = containerDiv;
                }
            }
            disablePointerEvents();
        }
        if (clearOnMouseDown && !(ctrlSel && ctrlKeyPressed) && !(shiftSel && shiftKeyPressed)) {
            selectedElms.clear()
        }
        if (clickSelect && mouseInContainer) {
            handleClickSelect(e.target)
        }
        if ((ctrlSel && ctrlKeyPressed) || (shiftSel && shiftKeyPressed)) {
            freezeSelection = new Set($selectedElms);
        }
        const sx = scrollContainer?.scrollLeft ?? 0
        const sy = scrollContainer?.scrollTop ?? 0
    }


    function handleMouseUp(){
        mouseDown = false;
        // mouseMove = false; //TODO: this probably shouldn't be here... can remove?
        selStartY = null;
        selStartX = null;
        if (!!selectDiv) {
            containerDiv.removeChild(selectDiv);
            selectDiv = null;
        }
        tempElms.clear();
        tempProcessedElms.clear();
        freezeSelection.clear();
        selectionIntercept.clear();

        enablePointerEvents();
    }
    function updateContainerDims() {
        containerDims = containerDiv.getBoundingClientRect()

    }

    function scrollContainerOnEdge(e) {
        if (!scrollContainer) return

        const scrollSpeed = 10
        const scrollArea = 5
        let scrollDeltaX = 0
        let scrollDeltaY = 0

        const scrollY = scrollContainer.scrollTop
        const scrollX = scrollContainer.scrollLeft
        const scrollBottom = scrollY + scrollContainer.clientHeight
        const scrollRight = scrollX + scrollContainer.clientWidth
        const mouseY = e.clientY
        const mouseX = e.clientX
        const containerTop = scrollContainerDims.top
        const containerBottom = scrollContainerDims.bottom
        const containerLeft = scrollContainerDims.left
        const containerRight = scrollContainerDims.right
        const scrollHeight = scrollContainer.scrollHeight
        const scrollWidth = scrollContainer.scrollWidth

        // vertical auto-scroll
        if (mouseY > containerBottom - scrollArea && scrollBottom < scrollHeight) {
            scrollContainer.scrollTop += scrollSpeed
            scrollDeltaY = scrollSpeed
        } else if (mouseY < containerTop + scrollArea && scrollY > 0) {
            scrollContainer.scrollTop -= scrollSpeed
            scrollDeltaY = -scrollSpeed
        }

        // horizontal auto-scroll
        if (mouseX > containerRight - scrollArea && scrollRight < scrollWidth) {
            scrollContainer.scrollLeft += scrollSpeed
            scrollDeltaX = scrollSpeed
        } else if (mouseX < containerLeft + scrollArea && scrollX > 0) {
            scrollContainer.scrollLeft -= scrollSpeed
            scrollDeltaX = -scrollSpeed
        }
        updateContainerDims();

    }



    function selectAllHandler(){
        if (!allSelected) {
            $selectedElms = new Set(selectableElements);
            allSelected = true;
        } else {
            selectedElms.clear();
            allSelected = false;
        }
    }

    function handleClickSelect(elm) {
        const allowedElementSet = new Set(selectableElements);

        if (allowedElementSet.has(elm)) {
            if (ctrlSel && ctrlKeyPressed) {
                // toggle selection
                if (selectedElms.has(elm)) {
                    selectedElms.delete(elm); // deselect if already selected
                } else {
                    selectedElms.add(elm); // add if not selected
                }
            } else if (shiftSel && shiftKeyPressed) {
                // shift-select logic (range selection)
                const selElmArr = [...$selectedElms];
                const firstSelectedIndex = selectableElements.indexOf(selElmArr[0]);
                const elmArrIdx = selectableElements.indexOf(elm);

                if (selElmArr.length === 0) {
                    selectedElms.add(elm);
                    return;
                }

                const firstSelectionElm = Math.min(elmArrIdx, firstSelectedIndex);
                const lastSelectionElm = Math.max(elmArrIdx, firstSelectedIndex);

                for (const [index, e] of selectableElements.entries()) {
                    if (index >= firstSelectionElm && index <= lastSelectionElm) {
                        selectedElms.add(e);
                    } else if (selectedElms.has(e)) {
                        selectedElms.delete(e);
                    }
                }
            } else {
                // normal click: clear selection and add the clicked element
                selectedElms.clear();
                selectedElms.add(elm);
            }
        }
    }

    let tempProcessedElms = new Set(); // to track elements already handled during drag
    let selectionIntercept = new Set();
    let tempElms = new Set();
    let freezeSelection = new Set();

    function handleCtrlDragSelect() {
        // figure out what's been removed from the current drag area
        const remove = tempProcessedElms.difference(tempElms)
        // figure out what's newly intercepted from the original selection
        const intercepted = tempElms.intersection(freezeSelection)
        // figure out what's newly added
        const add = tempElms.difference(tempProcessedElms)

        tempProcessedElms = tempProcessedElms.difference(remove).union(add)

        const unintercepted = selectionIntercept.difference(tempElms).union(add);

        $selectedElms = $selectedElms
            .difference(intercepted.union(remove))
            .union(add)
            .union(unintercepted)

        selectionIntercept = selectionIntercept.union(intercepted).difference(unintercepted);
    }

    function handleShiftDragSelect() {
        selectionIntercept = freezeSelection.intersection(tempElms).union(selectionIntercept);
        const remove = selectionIntercept.difference(tempElms);
        $selectedElms = freezeSelection.union(tempElms).difference(remove);
    }

    function addToSelect(cond, elm) {
        if (cond) {
            if (!(ctrlSel && ctrlKeyPressed) && !(shiftSel && shiftKeyPressed)) {
                selectedElms.add(elm);
            } else {
                tempElms.add(elm);
            }
        } else if (selectedElms.has(elm)) {
           if (!(ctrlSel && ctrlKeyPressed) && !(shiftSel && shiftKeyPressed)) {
                selectedElms.delete(elm)
            } else {
               if (tempElms.has(elm)){
                   tempElms.delete(elm);
               }
           }
        } else {
            if (tempElms.has(elm)){
                tempElms.delete(elm);
            }
        }
        return cond;
    }

    // Below function can surely be optimized.
    function depthCalcChildren(elm) {
        const elmChildren = getElmChildren(elm);
        if (syncDepth === 0 || !elmChildren) {
            return;
        }

        if (syncDepth === 1) {
            return elmChildren;
        }

        let allChildren = [...elmChildren]

        // Should I really just dump everything into above array or should I keep parents and children together?
        for (let i=0; i<syncDepth; i++) {
            for (let child of allChildren){
                const childChildren = getElmChildren(child);
                if (childChildren) {
                    allChildren.push(...childChildren);
                }
            }
        }

        return allChildren;
    }

    function getElmChildren(elm) {
        const children = elm.children;
        if (children) {
            return children
        }
        console.error(`Element ${elm} has no children.`)
    }

    function getBoundingBoxes(elmArr){
        let boxMap = {};
        if (elmArr.length > 0) {
            for (let elm of elmArr) {
                boxMap[elm] = elm.getBoundingClientRect();
            }
        }
        return boxMap;
    }

    function checkOneBound(selectBox, elmBox, directionSel, directionRect, boolCheck){
        return boolCheck(selectBox[directionSel], elmBox[directionRect]);
        // console.log(`Checking ${direction}: selectBox=${selectBox[direction]}, elmBox=${elmBox[direction]}`);
        // return b;
    }

    function checkAllBounds(selectBox, dirsCheckMap) {
        let conditionCheck = null;
        if (!dirsCheckMap.values()) {
            console.error("DirsCheckMap values size error",dirsCheckMap.values().length)
            throw new Error("There should be exactly 3 key-value pairs in dirsCheckMap")
        }
        for (let [elmBox, {selDirs, rectDirs, checkConds}] of dirsCheckMap.entries()) {
            const check1 = selDirs.length === rectDirs.length;
            const check2 = selDirs.length === checkConds.length;
            const check3 = rectDirs.length === checkConds.length;
            if (!check1 || !check2 || !check3) {
                console.error("selDirs, rectDirs and checkConds should be of the same lengths.")
                throw new Error("selDirs, rectDirs and checkConds should be of the same lengths.")
            }
            const len = selDirs.length;
            for (let i=0; i< len; i++){
                if (conditionCheck === null) {
                    conditionCheck = checkOneBound(selectBox, elmBox, selDirs[i], rectDirs[i], checkConds[i]);
                } else {
                    conditionCheck = conditionCheck && checkOneBound(selectBox, elmBox, selDirs[i], rectDirs[i], checkConds[i]);
                }
            }
        }
        return conditionCheck;
    }

    const lessThan = (a, b) => a < b;
    const greaterThan = (a, b) => a > b;
    const lessThanOrEqual = (a, b) => a <= b;
    const greaterThanOrEqual = (a, b) => a >= b;

    function createElmDirsCheckMap(rects,selDirections, rectDirections, checkConditions) {
        const map = new Map();
        for (const rect of rects) {
            map.set(rect, {
                selDirs: selDirections,
                rectDirs: rectDirections,
                checkConds: checkConditions
            });
        }
        return map;
    }


    // TODO Don't quite like this. Could refactor into more concise and organized code. SO MANY LOOPS.
    function handleDragSelect() {
        if (selectDiv) {
            const selectBox = selectDiv.getBoundingClientRect();

            if (selectableElements.length > 0) {
                for (const elm of selectableElements) {

                    const elmRect = elm.getBoundingClientRect();

                    let checkConditions;
                    let selDirections;
                    let rectDirections;


                    // check based on the current selection mode
                    if (
                        selectMode === "engulf"
                        || (
                            (selectMode==="dual" || selectMode === "dual-reversed")
                            && (selDirection === "SE" || selDirection === "NE")
                        )
                    ) {
                        checkConditions = [
                            lessThanOrEqual,
                            greaterThanOrEqual,
                            lessThanOrEqual,
                            greaterThanOrEqual
                        ];
                        selDirections = ["top", "bottom", "left", "right"];
                        rectDirections = selDirections;

                    } else if (
                        selectMode === "intersect"
                        || (
                            (selectMode==="dual" || selectMode === "dual-reversed")
                            && (selDirection === "SW" || selDirection === "NW")
                        )
                    ) {
                        checkConditions = [lessThan, greaterThan, lessThan, greaterThan];
                        selDirections = ["top", "bottom", "left", "right"];
                        rectDirections = ["bottom", "top", "right", "left"];
                }
                    let elmDirsCheckMap = createElmDirsCheckMap([elmRect], selDirections, rectDirections, checkConditions);

                    let elmSelected = checkAllBounds(selectBox, elmDirsCheckMap);


                    if (!elmSelected && syncDepth > 0) {
                        const elmChildrenWithRects = getBoundingBoxes(depthCalcChildren(elm));
                        elmDirsCheckMap = createElmDirsCheckMap(Object.values(elmChildrenWithRects), selDirections, rectDirections, checkConditions);
                        // console.log(elmDirsCheckMap);

                        for (let _ of Object.keys(elmChildrenWithRects)) {

                            elmSelected = checkAllBounds(selectBox, elmDirsCheckMap);
                            if (elmSelected) {
                                break;
                            }
                        }
                    }
                    addToSelect(elmSelected, elm);
                }
                if (ctrlSel && ctrlKeyPressed) {
                    handleCtrlDragSelect($selectedElms);
                } else if (shiftSel && shiftKeyPressed) {
                    handleShiftDragSelect($selectedElms);
                }
            }
            return onSelect(selectedElms);
        }
    }

    onMount(()=> {
        window.addEventListener("mousedown", handleMouseDown);
        window.addEventListener("mouseup", handleMouseUp);
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("resize", updateContainerDims);

    })

    onDestroy(()=>{
        window.removeEventListener("mousedown", handleMouseDown);
        window.removeEventListener("mouseup", handleMouseUp);
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("resize", updateContainerDims);
        if (ctrlSel || shiftSel) {
            window.removeEventListener("keydown", handleKeyDown);
            window.removeEventListener("keyup", handleKeyUp);
        }
    })

</script>
