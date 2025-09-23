import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { IconButton, TextField, Menu, MenuItem } from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import PaletteIcon from "@material-ui/icons/Palette";
import { Colorset } from "./Colorset";
import "./WeeklyProgram.css";
import {
  handleChangeDontFillColor,
  handleChangeDontFillDescription,
  handleDontFillDelete,
} from "./slices/dontFillsSlice";

export const DontFillBlock = ({ data }) => {
  const [editing, setEditing] = useState(false);
  const [localTitle, setLocalTitle] = useState(data.title); // Local state for editing
  const [anchorEl, setAnchorEl] = useState(null);
  const [containerRef, setContainerRef] = useState(null);
  const [isCompact, setIsCompact] = useState(true); // Start with compact as default
  const [showControls, setShowControls] = useState(false); // Show buttons only when active
  const dispatch = useDispatch();

  const colorset = new Colorset();
  const colors = colorset.colors;
  const open = Boolean(anchorEl);

  const handleOpenColorPalette = (event) => {
    setAnchorEl(event.currentTarget);
    setShowControls(true);
  };

  const handleColorSelect = (color) => {
    dispatch(
      handleChangeDontFillColor({ startDate: data.startDate, color: color })
    );
    handleClose();
  };
  const handleDeleteDontFill = () => {
    dispatch(handleDontFillDelete({ startDate: data.startDate }));
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  // Sync local title with props when not editing
  React.useEffect(() => {
    if (!editing) {
      setLocalTitle(data.title);
    }
  }, [data.title, editing]);

  const handleDescriptionChange = (e) => {
    setLocalTitle(e.target.value); // Update local state only
  };

  const handleTextFieldKeyDown = (e) => {
    if (e.keyCode === 13) {
      handleStopEditing();
    }
  };

  const handleStartEditing = () => {
    setLocalTitle(data.title); // Initialize local state with current value
    setEditing(true);
    setShowControls(true);
  };

  const handleStopEditing = () => {
    // Update Redux state when editing finishes
    if (localTitle !== data.title) {
      dispatch(
        handleChangeDontFillDescription({
          startDate: data.startDate,
          description: localTitle,
        })
      );
    }
    setEditing(false);
  };

  // Check container height to determine layout
  React.useEffect(() => {
    if (containerRef && !editing) { // Only check height when not editing
      const checkHeight = () => {
        const height = containerRef.clientHeight;
        // If height is less than 60px, use compact layout
        setIsCompact(height < 60);
      };
      
      checkHeight();
      
      // Check on resize, but debounce it
      let timeoutId;
      const debouncedCheckHeight = () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(checkHeight, 100);
      };
      
      const resizeObserver = new ResizeObserver(debouncedCheckHeight);
      resizeObserver.observe(containerRef);
      
      return () => {
        resizeObserver.disconnect();
        clearTimeout(timeoutId);
      };
    }
  }, [containerRef, editing]); // Add editing to dependencies

  // Hide controls when clicking outside the block (unless palette open or editing)
  React.useEffect(() => {
    if (!containerRef) return;
    const handleDocumentMouseDown = (e) => {
      if (
        containerRef &&
        !containerRef.contains(e.target) &&
        !open &&
        !editing
      ) {
        setShowControls(false);
      }
    };
    document.addEventListener("mousedown", handleDocumentMouseDown);
    return () => document.removeEventListener("mousedown", handleDocumentMouseDown);
  }, [containerRef, open, editing]);

  return (
    <div 
      ref={setContainerRef}
      className={`program-text-container-df ${isCompact ? 'compact-layout' : 'expanded-layout'}`}
      onClick={() => setShowControls(true)}
    >
      {isCompact ? (
        // Compact single-row layout for small cells
        <div className="df-single-row">
          {showControls && (
            <IconButton 
              className="df-control-button df-delete-button compact"
              onClick={handleDeleteDontFill}
            >
              <CloseIcon style={{ color: '#ffffff' }} />
            </IconButton>
          )}
          {editing ? (
            <TextField
              value={localTitle}
              className="df-description-text-field-compact"
              InputProps={{ 
                style: { color: data.color.text },
                disableUnderline: true
              }}
              variant="standard"
              onChange={handleDescriptionChange}
              onKeyDown={handleTextFieldKeyDown}
              onBlur={handleStopEditing}
              autoFocus
            />
          ) : (
            <div
              className="program-title-dont-fill-compact"
              style={{ color: data.color.text }}
              onClick={handleStartEditing}
              title={data.title}
            >
              {data.title}
            </div>
          )}
          {showControls && (
            <IconButton
              className="df-control-button df-palette-button compact"
              id="palette-button"
              aria-controls={open ? "palette-menu" : undefined}
              aria-haspopup="true"
              aria-expanded={open ? "true" : undefined}
              onClick={handleOpenColorPalette}
            >
              <PaletteIcon style={{ color: '#ffffff' }} />
            </IconButton>
          )}
        </div>
      ) : (
        // Expanded two-row layout for larger cells
        <>
          {showControls && (
            <div className="df-controls-row">
              <IconButton 
                className="df-control-button df-delete-button"
                onClick={handleDeleteDontFill}
              >
                <CloseIcon style={{ color: '#ffffff' }} />
              </IconButton>
              <IconButton
                className="df-control-button df-palette-button"
                id="palette-button"
                aria-controls={open ? "palette-menu" : undefined}
                aria-haspopup="true"
                aria-expanded={open ? "true" : undefined}
                onClick={handleOpenColorPalette}
              >
                <PaletteIcon style={{ color: '#ffffff' }} />
              </IconButton>
            </div>
          )}
          <div className="df-title-row">
            {editing ? (
              <TextField
                value={localTitle}
                className="df-description-text-field-expanded"
                InputProps={{ 
                  style: { color: data.color.text },
                  disableUnderline: true
                }}
                variant="standard"
                onChange={handleDescriptionChange}
                onKeyDown={handleTextFieldKeyDown}
                onBlur={handleStopEditing}
                autoFocus
              />
            ) : (
              <div
                className="program-title-dont-fill-expanded"
                style={{ color: data.color.text }}
                onClick={handleStartEditing}
                title={data.title}
              >
                {data.title}
              </div>
            )}
          </div>
        </>
      )}
      
      <Menu
        id="palette-menu"
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "palette-button",
        }}
        PaperProps={{
          style: {
            backgroundColor: "black",
          },
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "5px",
            padding: "5px",
            paddingTop: "0px",
            paddingBottom: "0px",
            backgroundColor: "black",
          }}
        >
          {colors.map((color) => (
            <MenuItem
              key={color.main}
              onClick={() => handleColorSelect(color)}
              style={{ padding: 0 }}
            >
              <div
                style={{
                  width: "30px",
                  height: "30px",
                  backgroundColor: color.main,
                  borderRadius: "4px",
                }}
              ></div>
            </MenuItem>
          ))}
        </div>
      </Menu>
    </div>
  );
};
